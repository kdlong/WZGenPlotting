#!/usr/bin/env python
import plot_functions as plotter
import argparse
import ROOT
import config_object

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--root_file", type=str, required=True,
                        help="Name of root file where plots are stored")
    parser.add_argument("-o", "--output_file", type=str, required=True,
                        help="Name of file to be created (type pdf/png etc.)")
    parser.add_argument("-n", "--cutflow_name", type=str, required=False,
                        help="Name of cut flow in cutflow.json config file")
    return parser.parse_args()
def getCutFlowHist(root_file_name, config, name_in_config):
    root_file = ROOT.TFile(root_file_name)                          
    cutflow_hist = plotter.getHistFromFile(root_file, "cutflow", 
                                           name_in_config, "")                                                                  
    cutflow_hist.Draw()
    config.setAttributes(cutflow_hist, name_in_config)
    return cutflow_hist

def stackFromConfig(config, root_file_name):
    hist_stack = ROOT.THStack("cutflow stack", "cutflow stack")
    for hist_name in config.getListOfHists(): 
        hist = getCutFlowHist(
            root_file_name.replace(".", hist_name.replace("cutflow", "") + "."), 
            config,
            hist_name)
        hist_stack.Add(hist)
    print root_file_name.replace(".", hist_name.replace("cutflow", "") + "."), 
    return hist_stack
def main():
    ROOT.gROOT.SetBatch(True)
    args = getComLineArgs()
    config_file = "/cms/kdlong/WZxsec/InitialStateAnalysis/" \
                  "my_plotting/config_files/cutflows.json"
    config = config_object.ConfigObject(config_file)
    canvas = config.getCanvas()
    
    hist_stack = ROOT.THStack("cutflow stack", "cutflow stack")
    hist = getCutFlowHist(args.root_file, config,  args.cutflow_name)                                                                                                                         
    # Abitrarily scaled the same :(
    # Fiducial
    # Trigger Pts  
    # Duplicate    
    # Duplicate    
    # 3l           
    # Z            
    # W            
    genvals = [237484,
            68272,  
            54764,  
            54764,  
            46428,  
            42463,  
            32152]  
    gen_hist = ROOT.TH1F("cutflow_gen", "cutflow_gen", 8, 0, 8)
    for i, val in enumerate(genvals):
        gen_hist.SetBinContent(i + 1, val)
    config.setAttributes(gen_hist, "cutflow_gen")
    hist_stack.Add(hist)
    hist_stack.Add(gen_hist)
    hist_stack.Draw("nostack")
    hist_stack.SetTitle("")
    hist_stack.GetXaxis().SetRange(1, 8)    
    hist_stack.GetYaxis().SetTitleSize(0.035)    
    hist_stack.GetYaxis().SetTitleOffset(1.1)    
    hist_stack.GetYaxis().SetTitle("Events Passing Selection")    
    hist_stack.GetHistogram().SetLabelSize(0.04)
    hist_stack.GetXaxis().SetLabelOffset(0.011)
    
    legend = ROOT.TLegend(.55, .75, .88, .88)

    name = {}
    name['cutflow'] = "Reconstructed"
    name['cutflow_gen'] = "Gen-level"
    for hist in hist_stack.GetHists():
        legend.AddEntry(hist, name[hist.GetName()], "f")
    legend.SetFillColor(0)
    legend.Draw()

    canvas.Print(args.output_file)                                                                                       

if __name__ == "__main__":
    main()
