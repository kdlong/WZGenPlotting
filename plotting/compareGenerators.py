#!/usr/bin/env python
import Utilities.plot_functions as plotter
import argparse
import ROOT
import config_object
import json
import Utilities.selection as selection

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_file", type=str, required=True,
                        help="Name of file to be created (type pdf/png etc.) " \
                        "Note: 'NAME' will be replaced by branch name")
    parser.add_argument("-s", "--scale", type=str, default="xsec",
                        help="Method for scalling hists")
    parser.add_argument("-r", "--make_ratio", action="store_true",
                        help="Add ratio comparison")
    parser.add_argument("--legend_left", action="store_true",
                        help="Put legend left or right")
    parser.add_argument("--fiducial_cuts", type=str, default="",
                        help="Apply fiducial cuts before plotting")
    parser.add_argument("-c","--channel", type=str, default="",
                        help="Plot specifc channel")
    parser.add_argument("--no_errors", action="store_true",
                        help="Don't plot error bands")
    parser.add_argument("-b", "--branches", type=str,
                        help="List (separate by commas) of names of branches "
                        "in root and config file to plot")
    parser.add_argument("-f", "--files_to_plot", type=str, required=False,
                        default="", help="Files to make plots from, "
                        "separated by a comma (match name in file_info.json)")
    return parser.parse_args()
def getHist(root_file_name, config, hist_name, name_in_config):
    root_file = ROOT.TFile(root_file_name)                          
    hist = plotter.getHistFromFile(root_file, 
            "".join([hist_name, "_", name_in_config]), 
            name_in_config, "")                                                                  
    hist.Draw("hist")
    config.setAttributes(hist, name_in_config)
    return hist

def getStacked(file_info, files_to_plot, path_to_tree, branch_name, cut_string, scale):
    hist_stack = ROOT.THStack("stack", "")
    for name, entry in file_info.iteritems():
        if files_to_plot != "" and entry["name"] not in [x.strip() for x in files_to_plot.split(",")]:
            continue
        config = config_object.ConfigObject(
                "./config_files/" + entry["plot_config"])
        name = ''.join([entry["name"], "-", branch_name])
        hist = config.getObject(name, entry["title"])

        root_file = ROOT.TFile(entry["filename"])
        if not root_file:
            print 'Failed to open %s' % root_file
            exit(0)
        plotter.loadHistFromTree(hist, 
            root_file, 
            path_to_tree,
            branch_name,
            cut_string
        )
        config.setAttributes(hist, name)
        print "Title is %s" % hist.GetTitle()
        if scale == "xsec":
            scaleHistByXsec(hist, root_file, 10000)
        elif scale == "unity":
            print "Scalling hists in stack to unity"
            hist.Sumw2()
            print "hist has %i entries" % hist.GetEntries()
            hist.Scale(1/hist.GetEntries())
        else:
            print "No scalling applied!"
        hist_stack.Add(hist, "hist")
    return hist_stack
def scaleHistByXsec(hist, root_file, lumi):
    metadata = root_file.Get("analyzeWZ/MetaData")
    for row in metadata:
        numEvents = row.nPass
        xSec = row.fidXSection
        print "The fiducial x section was %f" % xSec
    scale_factor = xSec/numEvents*lumi
    new_fidXSec = xSec*hist.GetEntries()/numEvents
    print "%i initial events, %i selected events" % (numEvents, hist.GetEntries())
    print "The new fiducial cross section is %f" % new_fidXSec 
    print "Scaled by %s" % scale_factor
    hist.Sumw2()
    hist.Scale(scale_factor)

def getFileInfo():
    with open("./config_files/file_info.json") as json_file:    
        file_info = json.load(json_file)
    return file_info

def getCutString(args, branch_name):
    cut_string = ""
    if "j1" in branch_name:
        cut_string = "j1Pt > 0"
    elif "j2" in branch_name:
        cut_string = "j2Pt > 0"
    if args.fiducial_cuts != "":
        if cut_string != "":
            cut_string += " && " 
        if args.fiducial_cuts == "all":
            cut_string += selection.getFiducialCutString("WZ")
        elif args.fiducial_cuts == "zMass":
            cut_string += selection.getZMassCutString(1)
    if args.channel != "":
        if cut_string != "":
            cut_string += " && "
        cut_string += getattr(selection, "getChannel%sCutString" % args.channel.upper())()
    return cut_string
def plotStack(file_info, args, branch_name):
    canvas = ROOT.TCanvas("canvas", "canvas", 800, 600) 

    cut_string = getCutString(args, branch_name)
    hist_stack = getStacked(file_info, args.files_to_plot,
        "analyzeWZ/Ntuple", branch_name, cut_string, args.scale)
    hists = hist_stack.GetHists()
    
    hist_stack.Draw("nostack")
    hist_stack.GetYaxis().SetTitleSize(0.040)    
    hist_stack.GetYaxis().SetTitleOffset(1.3)    
    hist_stack.GetYaxis().SetTitle( 
        hists[0].GetYaxis().GetTitle())
    hist_stack.GetXaxis().SetTitle(
        hists[0].GetXaxis().GetTitle())
    #hist_stack.GetHistogram().SetLabelSize(0.04)
    print "The title should be %s" % hist_stack.GetHistogram().GetXaxis().GetTitle()
    
    xcoords = [.15, .55] if args.legend_left else [.55, .95]
    legend = ROOT.TLegend(xcoords[0], 0.8, xcoords[1], 0.9)
    legend.SetFillColor(0)
    histErrors = []
    
    for hist in hists:
        legend.AddEntry(hist, hist.GetTitle(), "f")
        if not args.no_errors:
            histErrors.append(plotter.getHistErrors(hist, hist.GetLineColor()))
            histErrors[-1].Draw("E2 same")
    legend.Draw()
    
    output_file_name = args.output_file.replace("NAME", branch_name) 
    if args.make_ratio:
        split_canvas = plotter.splitCanvas(canvas, "stack", "01j FxFx", "incl")
        split_canvas.Print(output_file_name)
    else:
        canvas.Print(output_file_name)

def main():
    #ROOT.gROOT.SetBatch(True)
    args = getComLineArgs()
    file_info = getFileInfo()
    branches = [x.strip() for x in args.branches.split(",")]
 
    for branch in branches:
        plotStack(file_info, args, branch)


if __name__ == "__main__":
    main()
