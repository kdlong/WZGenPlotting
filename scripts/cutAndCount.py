#!/usr/bin/env python
import argparse
import sys
import datetime
import ROOT
import Utilities.plot_functions as plotter
import Utilities.helper_functions as helper
import Utilities.WeightInfo as WeightInfo
import Utilities.WeightedHistProducer as WeightedHistProducer

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
        print filename
        metaTree = plotter.buildChain(filename, "analyze%s/MetaData" % args.analysis) 
        weight_info = WeightInfo.WeightInfoProducer(metaTree, "fidXSection", "fidSumWeights").produce()

        ntuple = plotter.buildChain(filename, "analyze%s/Ntuple" % args.analysis) 
        histProducer = WeightedHistProducer.WeightedHistProducer(ntuple, weight_info, "weight")  
        histProducer.setLumi(1)

        cut_string = helper.getCutString(args.default_cut, args.channel, args.make_cut)
        
        histname = "l1Pt-" + name
        hist = ROOT.TH1F(histname, histname, 100, 0, 1000)
        histProducer.produce(hist, "l1Pt", "", args.max_entries)
        initialXsec = hist.Integral()
        histProducer.produce(hist, "l1Pt", cut_string, args.max_entries)
        selectedXsec = hist.Integral()
    
        total_processed = 0
        for row in metaTree:
            total_processed += row.nProcessedEvents

        print "_______________________________________________________________\n"
        print "Results for file: %s\n" % filename
        print "Total Number of events processed: %i" % total_processed 
        print "Initial selection cross section is %f " % initialXsec
        print "Selection cross section is %f " % selectedXsec

    print "_______________________________________________________________"
    print "\nSelections made using cut string:"
    print cut_string
    print "_______________________________________________________________"
if __name__ == "__main__":
    main()
