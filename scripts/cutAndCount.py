#!/usr/bin/env python
import argparse
import ROOT
import Utilities.selection as selection

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--apply_cut", type=str, default="",
                        help="Enter a valid root cut string to apply")
    parser.add_argument("-d","--default_cuts", type=str, default="",
                        choices=['', 'WZ fid', 'zMass'],
                        help="Apply default cut string.")
    parser.add_argument("-c","--channel", type=str, default="",
                        choices=['eee', 'eem', 'emm', 'mmm'],
                        help="Apply default cut string.")
    input = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument("-f", "--input_file", type=str,
                        default="", help="File with WZNutple to run over")
    #parser.add_argument("-l", "--input_files", type=str,
    #                    default="", help="File with WZNutple to run over")
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
    if args.apply_cut != "":
        cut_string = append_cut(cut_string, args.apply_cut)
    return cut_string

def main():
    ROOT.gROOT.SetBatch(True)
    args = getComLineArgs()
    if os.path.isfile(args.input_file):
        root_file = ROOT.TFile(args.input_file)
        metaTree = root_file.Get("analyzeWZ/MetaData")
        ntuple = root_file.Get("analyzeWZ/Ntuple")
    else:
        ntuple = buildChain("analyzeWZ/Ntuple", glob.glob(args.input_file))
        metaTree = buildChain("analyzeWZ/MetaData", glob.glob(args.input_file))
    xsec = {}
    events = {}
    for row in metaTree:
        xsec["total"] = row.inputXSection
        xsec["initial_selection"] = row.fidXSection
        events["total"] = row.nProcessedEvents
        events["initial_selection"] = row.nPass
    
    cut_string = getCutString(args, "l1Pt")
    events["selection"] = ntuple.Draw("l1Pt", cut_string)
    xsec["selection"] = xsec["total"]*events["selection"]/events["total"]
    
    print "_______________________________________________________________\n"

    print "%i events in inital sample" % events["total"]
    print "%i events passed initial selection" % events["initial_selection"]
    print "%i events passed Selection" % events["selection"]

    print "\nTotal gen cross section is %f " % xsec["total"]
    print "Initial selection cross section is %f " % xsec["initial_selection"]
    print "Selection cross section is %f " % xsec["selection"]    
    print "\nSelection made using cut string:"
    print cut_string
    print "\n_______________________________________________________________"

if __name__ == "__main__":
    main()
