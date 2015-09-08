import plot_functions as plotter
import Utilities.WeightInfo as WeightInfo
import Utilities.WeightedHistProducer as WeightedHistProducer
import Utilities.selection as selection
import ROOT
import json
import os
import glob

def append_cut(cut_string, cut):
    return ''.join([cut_string, "" if cut_string is "" else " && ", cut])
def getCutString(default, channel, user_cut):
    cut_string = ""
    if default == "WZ":
        cut_string = append_cut(cut_string, selection.getFiducialCutString("WZ", True))
    elif default == "zMass":
        cut_string = append_cut(cut_string, selection.getZMassCutString("WZ", True))
    if channel != "":
        cut_string = append_cut(cut_string, 
                getattr(selection, "getChannel%sCutString" % channel.upper())())
    if user_cut != "":
        cut_string = append_cut(cut_string, user_cut)
    return cut_string
def getHist(root_file_name, config, hist_name, name_in_config):
    root_file = ROOT.TFile(root_file_name)                          
    hist = plotter.getHistFromFile(root_file, 
            "".join([hist_name, "_", name_in_config]), 
            name_in_config, "")                                                                  
    hist.Draw("hist")
    config.setAttributes(hist, name_in_config)
    return hist
def getHistFromFile(root_file_name, config, hist_name, name_in_config):
    root_file = ROOT.TFile(root_file_name)                          
    hist = plotter.getHistFromFile(root_file, 
            "".join([hist_name, "_", name_in_config]), 
            name_in_config, "")                                                                  
    hist.Draw("hist")
    config.setAttributes(hist, name_in_config)
    return hist
def getFileInfo(info_file):
    with open(info_file) as json_file:    
        file_info = json.load(json_file)
    return file_info
def getHistFactory(info_file, filelist, analysis):
    all_files = getFileInfo(info_file)
    file_info = {}
    for name in filelist:
        print "Name is %s at initialization" % name
        if name not in all_files.keys():
            print "%s is not a valid file name (must match a definition in %s)" % (filename, info_file)
            continue
        file_info[name] = dict(all_files[name])
        metaTree = plotter.buildChain(file_info[name]["filename"], 
                "analyze%s/MetaData" % analysis) 
        weight_info = WeightInfo.WeightInfoProducer(metaTree, "fidXSection", "fidSumWeights").produce()
        ntuple = plotter.buildChain(file_info[name]["filename"], 
                "analyze%s/Ntuple" % analysis) 
        histProducer = WeightedHistProducer.WeightedHistProducer(ntuple, weight_info, "weight")  
        file_info[name]["histProducer"] = histProducer
    return file_info
#def getTrueWHist(hist, histProducer, cut, max_events):
#    
#    cut = ''.join(["((", cut.replace("W, W1"), ") && (W1isTrueW))")] 
#    producer.produce(hist, to_plot.replace("W", "W1"), cut_string, max_entries)
#
def getChain(filelist, path_to_tree):
    filelist = glob.glob(filelist)
    tree = ROOT.TChain(path_to_tree)
    for file_name in filelist:
        tree.Add(file_name)
    return tree
