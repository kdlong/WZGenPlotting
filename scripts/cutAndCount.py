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

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--make_cut", type=str, default="",
                        help="Enter a valid root cut string to apply")
    parser.add_argument("-a", "--analysis", type=str, choices=["WZ", "ZZ"],
                        required=True, help="Analysis: WZ or ZZ")
    parser.add_argument("-d","--default_cut", type=str, default="",
                        choices=['', 'WZ', 'zMass'],
                        help="Apply default cut string.")
    parser.add_argument("-c","--channel", type=str, default="",
                        choices=['eee', 'eem', 'emm', 'mmm',
                                 'eeee', 'eemm', 'mmmm'],
                        help="Select only one channel")
    parser.add_argument("-n", "--max_entries", type=int, default=-1,
                        help="Draw only first n entries of hist "
                        "(useful for huge root files)")
    parser.add_argument("-u", "--scale_uncertainty", action='store_true',
                        help="Print scale uncertainties")
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
    histname = "l1Pt-" + name
    hist = ROOT.TH1F(histname, histname, 100, 0, 1000)
    histProducer.produce(hist, "l1Pt", "", max_entries)
    initialXsec = hist.Integral()
    histProducer.produce(hist, "l1Pt", cut_string, max_entries)
    selectedXsec = hist.Integral()
    return (initialXsec, selectedXsec)
def getWeightMap(weight_ids):
    scales = ["uR = 1, uF = 1", "uR = 1, uF = 2", "uR = 1, uF = 1/2", "uR = 2, uF = 1",
              "uR = 2, uF = 2", "uR = 2, uF = 1/2", "uR = 1/2, uF = 1", "uR = 1/2, uF = 2",
              "uR = 1/2, uF = 1/2"]
    weight_map = {}
    for i, weight_id in enumerate(weight_ids):
        if weight_id in [ "100%i" % (j+1) for j in range(0, len(scales))]:
            weight_map[weight_ids[i]] = scales[i]
        else:
            weight_map[weight_ids[i]] = weight_ids[i]

    table = PrettyTable(["LHA PDF ID", "Initial x-sec", "Selected x-sec"])
    table.set_field_align("LHA PDF ID", "l") # Left align
    return weight_map
def getScalePDFVariations(histProducer, weight_ids, name, cut_string, max_entries):
    printValues = True
    #weight_map = getWeightMap(weight_ids)
    table = PrettyTable(["Weight ID", "Initial x-sec", "Selected x-sec"])
    table.set_padding_width(1)
    values = {"init" : {}, "select" : {}}
    for weight in weight_ids:
        if "001" in weight:
            values["init"][weight] = []
            values["select"][weight] = []
    for i, weight_id in enumerate(weight_ids):
        histProducer.setWeightBranch("weight*LHEweights[%i]/XWGTUP" % i)
        (initialXsec, selectedXsec) = getCrossSections(histProducer, name, cut_string, max_entries)
        table.add_row([weight_ids[i], initialXsec, selectedXsec])
        scale_type = "scale" if weight_ids[i] in [ "100%i" % i for i in range(1, 11)] else "pdf"
        label = str(weight_id[0]) + "001" 
        values["init"][label].append(initialXsec)
        values["select"][label].append(selectedXsec)
#    centrals = []
#    for selection, value_map in values.iteritems():
#        print selection
#        central = value_map["1001"][0]
#        for weight, value in value_map.iteritems():
#            if central != value[0]:
#                print "Central values not equal!"
#                print "Central value for 1001 is: %f " % central
#                print "Central value for %s is: %f " % (weight, value[0])
#                exit(0)
    if printValues:
        print table
    return values
def getScaleUncertainty(values):
    scale_info = {}
    for select in ["init", "select"]:
        central = values["%s" % select]["1001"][0]
        scale_info['%s_down' % select] = (1-min(values[select]["1001"])/central)*100
        scale_info['%s_up' % select] = (max(values[select]["1001"])/central - 1)*100
    return scale_info
def getPDFUncertainty(values):
    pdf_unc = { "init" : {}, "select" : {} }
    for selection, value_map in values.iteritems():
        for pdf_set in value_map:
            print pdf_set
            if "1001" not in pdf_set:
                pdf_unc[selection][pdf_set] = 0
    for selection in pdf_unc:
        for pdf_set in pdf_unc[selection]:
            print pdf_set
            variance = 0
            central = values[selection]["1001"][0]
            print central
            for value in values[selection][pdf_set][1:]:
                variance += (value - central)*(value - central)
            num = len(values[selection][pdf_set]) - 2
            print variance
            pdf_unc[selection][pdf_set] = math.sqrt(variance/(num))/central*100
            print pdf_unc
    print pdf_unc
    return pdf_unc
def main():
    ROOT.gROOT.SetBatch(True)
    args = getComLineArgs()

    print 'Script called at %s' % datetime.datetime.now()
    print 'The command was: %s\n' % ' '.join(sys.argv)

    file_info = helper.getFileInfo("../plotting/config_files/file_info.json")
    for name in args.filenames.split(","):
        name = name.strip()
        if name in file_info.keys():
            filename = file_info[name]["filename"]
        else:
            filename = name
            name = "input"
        print filename
        metaTree = plotter.buildChain(filename, "analyze%s/MetaData" % args.analysis) 
        weight_info = WeightInfo.WeightInfoProducer(metaTree, "fidXSection", "fidSumWeights").produce()

        total_processed = 0
        weight_ids = []
        for row in metaTree:
            total_processed += row.nProcessedEvents
            weight_ids = row.LHEweightIDs 
        ntuple = plotter.buildChain(filename, "analyze%s/Ntuple" % args.analysis) 
        histProducer = WeightedHistProducer.WeightedHistProducer(ntuple, weight_info, "weight")  
        histProducer.setLumi(1)
        cut_string = helper.getCutString(args.default_cut, args.channel, args.make_cut)
        
        (initialXsec, selectedXsec) = getCrossSections(histProducer, name, cut_string, args.max_entries)

        #if args.scale_uncertainty:
        variations = getScalePDFVariations(histProducer, weight_ids, name, cut_string, args.max_entries)
        scale_unc = getScaleUncertainty(variations)
        pdf_unc = getPDFUncertainty(variations)
        print "_______________________________________________________________\n"
        print "Results for file: %s\n" % filename
        print "Total Number of events processed: %i" % total_processed 
        print "Initial selection cross section is %f " % initialXsec
        if args.scale_uncertainty:
            print "    Scale variation (percent): +%0.1f%% -%0.1f%%" \
                % (scale_unc["init_up"], scale_unc["init_down"])
            print pdf_unc["init"]
            print "    PDF uncertainty (percent): +%0.1f%% -%0.1f%%" \
                % (pdf_unc["init"]["2001"], pdf_unc["init"]["2001"])
        print "Selection cross section is %f " % selectedXsec
        if args.scale_uncertainty:
            print "    Scale variation (percent): +%0.1f%% -%0.1f%%" \
                % (scale_unc["select_up"], scale_unc["select_down"])
            print "    PDF uncertainty (percent): +%0.1f%% -%0.1f%%" \
                % (pdf_unc["select"]["2001"], pdf_unc["select"]["2001"])

    print "_______________________________________________________________"
    print "\nSelections made using cut string:"
    print cut_string
    print "_______________________________________________________________"
if __name__ == "__main__":
    main()
