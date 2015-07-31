#!/usr/bin/env python
import argparse
import ROOT
import Utilities.selection as selection
import Utilities.plot_functions as plotter
import Utilities.WeightInfo as WeightInfo
import Utilities.WeightedHistProducer as WeightedHistProducer

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--make_cut", type=str, default="",
                        help="Enter a valid root cut string to apply")
    parser.add_argument("-a", "--analysis", type=str, choices=["WZ", "ZZ"],
                        required=True, help="Analysis: WZ or ZZ")
    parser.add_argument("-d","--default_cuts", type=str, default="",
                        choices=['', 'WZ fid', 'zMass'],
                        help="Apply default cut string.")
    parser.add_argument("-c","--channel", type=str, default="",
                        choices=['eee', 'eem', 'emm', 'mmm'],
                        help="Apply default cut string.")
    parser.add_argument("-f", "--input_file", type=str, required=True,
                        default="", help="File with GenNutple to run over")
    return parser.parse_args()

def append_cut(cut_string, cut):
    if cut_string != "":
        cut_string += " && " 
    cut_string += cut
    return cut_string

def getCutString(args, branch_name):
    cut_string = ""
    if "j1" in branch_name:
        cut_string = "j1Pt > 0"
    elif "j2" in branch_name:
        cut_string = "j2Pt > 0"
    if args.default_cuts == "WZ fid":
        cut_string = append_cut(cut_string, selection.getFiducialCutString("WZ"))
    elif args.default_cuts == "zMass":
        cut_string = append_cut(cut_string, selection.getZMassCutString(1))
    if args.channel != "":
        cut_string = append_cut(cut_string, 
                getattr(selection, "getChannel%sCutString" % args.channel.upper())())
    if args.make_cut != "":
        cut_string = append_cut(cut_string, args.make_cut)
    return cut_string

def main():
    ROOT.gROOT.SetBatch(True)
    args = getComLineArgs()

    metaTree = plotter.buildChain(args.input_file, "analyze%s/MetaData" % args.analysis) 
    weight_info = WeightInfo.WeightInfoProducer(metaTree, "fidXSection", "fidSumWeights").produce()

    ntuple = plotter.buildChain(args.input_file, "analyze%s/Ntuple" % args.analysis) 
    histProducer = WeightedHistProducer.WeightedHistProducer(ntuple, weight_info, "weight")  
    histProducer.setLumi(1)

    cut_string = getCutString(args, "l1Pt")
    
    hist = ROOT.TH1F("hist", "hist", 100, 0, 1000)
    histProducer.produce(hist, "l1Pt")
    initialXsec = hist.Integral()
    histProducer.produce(hist, "l1Pt", cut_string)
    selectedXsec = hist.Integral()
    
    print "_______________________________________________________________\n"
    print "Initial selection cross section is %f " % initialXsec
    print "Selection cross section is %f " % selectedXsec
    print "\nSelection made using cut string:"
    print cut_string
    print "\n_______________________________________________________________"

if __name__ == "__main__":
    main()
