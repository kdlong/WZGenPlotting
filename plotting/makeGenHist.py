#!/usr/bin/env python
import plot_functions as plotter
import argparse
import ROOT
import config_object
import json
import Utilities.selection as selection

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_file", type=str, required=True,
                        help="Name of file to be created (type pdf/png etc.)")
    parser.add_argument("-s", "--scale", type=str, default="xsec",
                        help="Method for scalling hists")
    parser.add_argument("--fiducial_cuts", action="store_true",
                        help="Apply fiducial cuts before plotting")
    plot_group = parser.add_mutually_exclusive_group()
    plot_group.add_argument("-b", "--branch", type=str,
                        help="Name of branch in root and config file")
    plot_group.add_argument("-a", "--all", action="store_true")
    parser.add_argument("-f", "--file_to_plot", type=str, required=True,
                        default="", help="Files to make plots from, "
                        "separated by a comma (match name in file_info.json)")
    return parser.parse_args()
def getHistFromFile(root_file_name, config, hist_name, name_in_config):
    root_file = ROOT.TFile(root_file_name)                          
    hist = plotter.getHistFromFile(root_file, 
            "".join([hist_name, "_", name_in_config]), 
            name_in_config, "")                                                                  
    hist.Draw("hist")
    config.setAttributes(hist, name_in_config)
    return hist

def getHist(file_info, file_to_plot, path_to_tree, branch_name, cut_string, scale):
    for name, entry in file_info.iteritems():
        if entry["name"] not in file_to_plot.strip():
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
            scaleHistByXsec(hist, root_file, 1000)
        elif scale == "unity":
            print "Scalling hists in stack to unity"
            hist.Sumw2()
            hist.Scale(1/hist.GetEntries())
        else:
            print "No scalling applied!"
    return hist
def scaleHistByXsec(hist, root_file, lumi):
    metadata = root_file.Get("analyzeWZ/MetaData")
    for row in metadata:
        numEvents = row.nPass
        xSec = row.fidXSection
    scale_factor = xSec/numEvents*lumi
    print "Scaled by %s" % scale_factor
    hist.Sumw2()
    hist.Scale(scale_factor)

def getFileInfo():
    with open("./config_files/file_info.json") as json_file:    
        file_info = json.load(json_file)
    return file_info

def main():
    #ROOT.gROOT.SetBatch(True)
    args = getComLineArgs()
    file_info = getFileInfo()
    
    canvas = ROOT.TCanvas("canvas", "canvas", 1000, 600) 
    legendPad = ROOT.TPad('legendPad', 'ratioPad', 0.8, 0, 1., 1.)
    legendPad.Draw()
    histPad = ROOT.TPad('histPad', 'stackPad', 0., 0, 0.8, 1.)
    histPad.Draw()
    
    histPad.cd()
    if "j1" in args.branch:
        cut_string = "j1Pt > 0"
    elif "j2" in args.branch:
        cut_string = "j2Pt > 0"
    if args.fiducial_cuts:
        if cut_string != ""
            cut_string += " && " 
        cut_string += selection.getFiducialCutString("WZ")

    hist = getHist(file_info, args.file_to_plot, 
        "analyzeWZ/Ntuple", args.branch, cut_string, args.scale)
    hist.Draw("hist")
    histErrors = []
    histErrors.append(plotter.getHistErrors(hist, hist.GetLineColor()))
    histErrors[-1].Draw("E2 same")
    
    legendPad.cd()
    legend = ROOT.TLegend(0, 0.45, 1, 0.55)

    legend.AddEntry(hist, hist.GetTitle(), "f")
    legend.SetFillColor(0)
    legend.Draw()
    canvas.Print(args.output_file)

if __name__ == "__main__":
    main()
