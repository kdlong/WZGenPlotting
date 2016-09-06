import plot_functions as plotter
import Utilities.WeightInfo as WeightInfo
import Utilities.WeightedHistProducer as WeightedHistProducer
import Utilities.selection as selection
import ROOT
import json
import os
import glob

def getCrossSections(histProducer, name, cut_string):
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
def getMetaInfo(filename, analysis):
    metaInfo = {}
    metaTree = plotter.buildChain(filename, "analyze%s/MetaData" % analysis) 
    metaInfo["total_processed"] = 0
    metaInfo["cross_section"] = 0
    metaInfo["summed_weights"] = []
    metaInfo["initSumWeights"] = 0
    metaInfo["weight_ids"] = []
    for row in metaTree:
        if not metaInfo["summed_weights"]:
            metaInfo["summed_weights"] = [0]*len(row.initLHEweightSums)
            for i, weight_id in enumerate(row.initLHEweightSums):
                metaInfo["weight_ids"].append(row.LHEweightIDs[i])
        metaInfo["cross_section"] = row.inputXSection
        metaInfo["total_processed"] += row.nProcessedEvents
        metaInfo["initSumWeights"] += row.initSumWeights
        for i, weight in enumerate(row.initLHEweightSums):
            metaInfo["summed_weights"][i] += weight
    return metaInfo
def getCrossSectionsFromFile(filename, dataset_name, metaInfo, analysis, cut_string):
    metaTree = plotter.buildChain(filename, "analyze%s/MetaData" % analysis) 
    weight_info = WeightInfo.WeightInfo(metaInfo["cross_section"], metaInfo["initSumWeights"])
    histProducer = WeightedHistProducer.WeightedHistProducer(weight_info, "weight")  
    histProducer.setLumi(1)
    return getCrossSections(histProducer, dataset_name, cut_string)
def append_cut(cut_string, cut):
    return ''.join([cut_string, "" if cut_string is "" else " && ", cut])
def getCutString(default, analysis, channel, user_cut):
    cut_string = ""
    if "WZ" in default or "ZZ" in default:
        if "notrue" not in default:
            cut_string = append_cut(cut_string, selection.getFiducialCutString(default, True))
        else:
            cut_string = append_cut(cut_string, selection.getFiducialCutString(default, False))
    elif default == "zMass":
        cut_string = append_cut(cut_string, selection.getZMassCutString(analysis, True))
    elif default == "Z1mass":
        cut_string = append_cut(cut_string, selection.getZMassCutString(analysis, False))
    elif default == "zMass8TeV":
        cut_string = append_cut(cut_string, selection.getZMassCutString(analysis + "8TeV", True))
    elif default == "Z4l":
        cut_string = append_cut(cut_string, selection.getFiducialCutString("Z4l", True))
        cut_string = append_cut(cut_string, "(4lmass > 80 && 4lmass < 100)")
    elif default == "Z4lmass":
        cut_string = append_cut(cut_string, selection.getZMassCutString("Z4l", True))
        cut_string = append_cut(cut_string, "(4lmass > 80 && 4lmass < 100)")
    elif default == "noTaus":
        num_leps = 3 if analysis == "WZ" else 4
        return " && ".join(["abs(l%ipdgId) != 15 " % i for i in range(1, num_leps + 1)])
    if channel != "":
        cut_string = append_cut("(" + cut_string + ")" if cut_string != "" else "", 
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
def getHistFactory(info_file, filelist, analysis, use_proof):
    all_files = getFileInfo(info_file)
    file_info = {}
    for name in filelist:
        if name not in all_files.keys():
            print "%s is not a valid file name (must match a definition in %s)" % (filename, info_file)
            continue
        file_info[name] = dict(all_files[name])
        metaTree = plotter.buildChain(file_info[name]["filename"], 
                "analyze%s/MetaData" % analysis) 
        weight_info = WeightInfo.WeightInfoProducer(metaTree, "fidXSection", "fidSumWeights").produce()
        ntuple = plotter.buildChain(file_info[name]["filename"], 
                "analyze%s/Ntuple" % analysis) 
        if use_proof:
            ntuple.SetProof()
        histProducer = WeightedHistProducer.WeightedHistProducer(weight_info, "weight")  
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
