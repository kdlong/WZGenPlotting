#!/usr/bin/env python
import argparse
import math
import sys
import datetime
import ROOT
import Utilities.plot_functions as plotter
import Utilities.helper_functions as helper
import Utilities.WeightInfo as WeightInfo
import Utilities.WeightedHistProducer as WeightedHistProducer
from Utilities.prettytable import PrettyTable
import Utilities.scalePDFUncertainties as Uncertainty
from collections import OrderedDict

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--make_cut", type=str, default="",
                        help="Enter a valid root cut string to apply")
    parser.add_argument("-a", "--analysis", type=str, choices=["WZ", "ZZ"],
                        required=True, help="Analysis: WZ or ZZ")
    parser.add_argument("-d","--default_cut", type=str, default="",
                        choices=['ZZ', 'noTaus', 'WZ', 'zMass', 'ZZvar', 
                        'WZ8TeV', 'zMass8TeV'],
                        help="Apply default cut string.")
    parser.add_argument("-c","--channel", type=str, default="",
                        choices=['eee', 'eem', 'emm', 'mmm',
                                 'eeee', 'eemm', 'mmmm'],
                        help="Select only one channel")
    parser.add_argument("-n", "--max_entries", type=int, default=-1,
                        help="Draw only first n entries of hist "
                        "(useful for huge root files)")
    parser.add_argument("-u", "--uncertainty", action='store_true',
                        help="Include scale/PDF uncertainties")
    parser.add_argument("--print_scale", action='store_true',
                        help="Print all values for scale uncertainties")
    parser.add_argument("--print_pdf", action='store_true',
                        help="Print all values for pdf variations")
    parser.add_argument("-f", "--filenames", type=str, required=True,
                        default="", help="List of root files with " 
                        "GenNutple format to run over, separated by commas. "
                        "Can be either name in file_info.json or true "
                        "file name")
    args = parser.parse_args()
    if "WZ" in args.analysis and len(args.channel) not in [0, 3]:
        print "Valid channels for WZ are eee, emm, eem, and mmm"
        exit(1)
    elif "ZZ" in args.analysis and len(args.channel) not in [0,4]:
        print "Valid channels for ZZ are eeee, eemm, and mmmm"
        exit(1)
    return args
def getCrossSections(histProducer, name, cut_string, max_entries):
    initialXsec = histProducer.getCrossSection()
    entries = -1
    if cut_string is "":
        selectedXsec = initialXsec
    else:
        hist = ROOT.TH1F("hist", "hist", 100, 0, 1000)
        hist = histProducer.produce(hist, "l1Pt", cut_string, "-".join([name, "gen"]))
        selectedXsec = hist.Integral()
        entries = hist.GetEntries()
    return [initialXsec, selectedXsec, entries]
def main():
    args = getComLineArgs()
    ROOT.gROOT.SetBatch(True)
    ROOT.TProof.Open('workers=24')

    file_info = helper.getFileInfo("../plotting/config_files/file_info.json")
    for name in args.filenames.split(","):
        name = name.strip()
        if name in file_info.keys():
            if "*" in file_info[name]["filename"]:
                filename = file_info[name]["filename"].rstrip("/*") + "/*"
            else:
                filename = file_info[name]["filename"]
        else:
            filename = name
            name = "input"
        metaTree = plotter.buildChain(filename, "analyze%s/MetaData" % args.analysis) 
        weight_info = WeightInfo.WeightInfoProducer(metaTree, "inputXSection", "initSumWeights").produce()
#
        total_processed = 0
        summed_weights = []
        weight_ids = []
        for row in metaTree:
            if not summed_weights:
                summed_weights = [0]*len(row.LHEweightSums)
            total_processed += row.nProcessedEvents
            for i, weight in enumerate(row.LHEweightSums):
                summed_weights[i] += weight
            weight_ids = row.LHEweightIDs 
        #ntuple = plotter.buildChain(filename, "analyze%s/Ntuple" % args.analysis) 
        #ntuple.SetProof()
        histProducer = WeightedHistProducer.WeightedHistProducer(weight_info, "weight")  
        histProducer.setLumi(1)
        cut_string = helper.getCutString(args.default_cut, args.analysis, args.channel, args.make_cut)
        
        xsecs = getCrossSections(histProducer, name, cut_string, args.max_entries)
        cross_secs = {"init" : xsecs[0], "fid" :xsecs[1]}
        variations = {"init" : {}, "fid" : {}}
        scale_unc = {"init" : {}, "fid" : {}}
        pdf_unc = {"init" : {}, "fid" : {}}
        if args.uncertainty:
            for selection in ["init", "fid"]:
                if selection == "init" or cut_string == "":
                    variations = Uncertainty.getVariations(weight_ids, summed_weights) 
                else:
                    variations = Uncertainty.getVariations(weight_ids, 
                        Uncertainty.getFiducialWeightSums(name + "-gen", cut_string))
                scale_unc[selection] = Uncertainty.getScaleUncertainty(variations)
                pdf_unc[selection] = Uncertainty.getFullPDFUncertainty(variations)

        print "_______________________________________________________________\n"
        print 'Script called at %s' % datetime.datetime.now()
        print 'The command was: %s\n' % ' '.join(sys.argv)
        print "Results for file: %s\n" % filename
        print "Total Number of events processed: %i" % total_processed 
        print "Total Number of events selected: %i" % xsecs[2] if xsecs[2] > 0 else total_processed
        print "Initial cross section is %0.5f" % round(cross_secs["init"], 5)
        print "Selection cross section is %0.5f " % round(cross_secs["fid"], 5)
        if args.uncertainty:
            for selection in ["init", "fid"]:
                print "\nUncertainties for %s" % selection
                print "    Scale variation: +%0.5f -%0.5f" \
                    % (round(cross_secs[selection]*scale_unc[selection]["up"]/100, 5), \
                       round(cross_secs[selection]*scale_unc[selection]["down"]/100, 5))
                print "    Scale variation (percent): +%0.1f%% -%0.1f%%" \
                    % (round(scale_unc[selection]["up"], 1), \
                       round(scale_unc[selection]["down"], 1))
                print "    PDF uncertainty: +%0.4f -%0.4f" \
                    % (round(cross_secs[selection]*pdf_unc[selection]/100, 5), \
                       round(cross_secs[selection]*pdf_unc[selection]/100, 5))
                print "    PDF uncertainty (percent): +%0.1f%% -%0.1f%%" \
                    % (round(pdf_unc[selection], 1), round(pdf_unc[selection], 1))

    print "_______________________________________________________________"
    print "\nSelections made using cut string:"
    print cut_string
    print "_______________________________________________________________"
    if args.print_scale and args.uncertainty:
        central = variations["1001"]["1001"]
        xsec = cross_secs["fid"]*1000
        print "Explicit scale values for fiducial region (in fb) were:"
        scale_values = OrderedDict({"FacDownRenDown" : variations["1001"]["1009"]/central*xsec})
        scale_values["facUprenUp"] = variations["1001"]["1005"]/central*xsec
        scale_values["renDown"] = variations["1001"]["1007"]/central*xsec
        scale_values["facUp"] = variations["1001"]["1002"]/central*xsec
        scale_values["facDown"] = variations["1001"]["1003"]/central*xsec
        scale_values["renUp"] = variations["1001"]["1004"]/central*xsec
        format_string = " ".join(["{%i:^15}" %i for i in xrange(0,6)])
        print format_string.format(*scale_values.keys())
        print format_string.format(*[str(value) for value in scale_values.values()])
        print "_______________________________________________________________"
    if args.print_pdf and args.uncertainty:
        print "Explicit values from pdf variations for fiducial region (in fb) were:"
        central = variations["1001"]["1001"]
        xsec = cross_secs["fid"]*1000
        for weight_set in variations:
            if weight_set == "1001": 
                continue
            for key, value in variations[weight_set].iteritems():
                print "%s %s" % (key, value/variations["1001"]["1001"]*xsec)
            print "_______________________________________________________________"

if __name__ == "__main__":
    main()
