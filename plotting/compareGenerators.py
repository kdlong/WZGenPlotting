#!/usr/bin/env python
import plot_functions as plotter
import argparse
import ROOT
import config_object
import json

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_file", type=str, required=True,
                        help="Name of file to be created (type pdf/png etc.)")
    parser.add_argument("--no_scale", type=bool, default=False,
                        help="Don't scale plot(s) by cross section")
    #parser.add_argument("-n", "--plot_name", type=str, required=True,
    #                    help="Name of hist in root and config file")
    return parser.parse_args()
def getHist(root_file_name, config, hist_name, name_in_config):
    root_file = ROOT.TFile(root_file_name)                          
    hist = plotter.getHistFromFile(root_file, 
            "".join([hist_name, "_", name_in_config]), 
            name_in_config, "")                                                                  
    hist.Draw("hist")
    config.setAttributes(hist, name_in_config)
    return hist

def getStacked(file_info, path_to_tree, branch_name, cut_string, scale):
    hist_stack = ROOT.THStack("stack", "")
    for name, entry in file_info.iteritems():
        config = config_object.ConfigObject(
                "./config_files/" + entry["plot_config"])
        name = ''.join([entry["name"], "-", branch_name])
        hist = config.getObject(name, entry["title"])
        config.setAttributes(hist, name)

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
        if scale:
            scaleHistByXsec(hist, root_file, 10)
        hist_stack.Add(hist)
    return hist_stack
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
    ROOT.gROOT.SetBatch(True)
    args = getComLineArgs()
    file_info = getFileInfo()
    canvas = ROOT.TCanvas("canvas", "canvas", 800, 600) 
    
    hist_stack = getStacked(file_info, "analyzeWZ/Ntuple", "zMass", "", True)
    hist_stack.Draw("nostack hist")
    hist_stack.GetYaxis().SetTitleSize(0.035)    
    hist_stack.GetYaxis().SetTitleOffset(1.2)    
    hist_stack.GetYaxis().SetTitle("Events")    
    hist_stack.GetXaxis().SetTitle("M_{Z} [GeV]")    
    hist_stack.GetXaxis().SetTitleOffset(1.2)    
    #hist_stack.GetHistogram().SetLabelSize(0.04)
    #hist_stack.GetXaxis().SetLabelOffset(0.01)

    legend = ROOT.TLegend(.55, .75, .88, .88)

    for hist in hist_stack.GetHists():
        legend.AddEntry(hist, hist.GetTitle(), "f")
    legend.SetFillColor(0)
    legend.Draw()
    canvas.SetRightMargin(1.2)
    canvas.Print(args.output_file)

if __name__ == "__main__":
    main()
