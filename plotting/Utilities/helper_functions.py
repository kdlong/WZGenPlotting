import plot_functions as plotter
import ROOT
import json
import os
import glob

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
def getFileInfo():
    with open("./config_files/file_info.json") as json_file:    
        file_info = json.load(json_file)
    return file_info
def loadHistFromTree(hist, filename, path_to_tree, branch_name, cut_string="", 
        max_entries=-1, append=False):
        if os.path.isfile(filename):
            root_file = ROOT.TFile(filename)
            if not root_file:
                print 'Failed to open %s' % root_file
                exit(0)
            print "So we made it here"
            plotter.loadHistFromTree(hist, 
                root_file, 
                path_to_tree,
                branch_name,
                cut_string,
                max_entries,
                append
            )
        elif "*" in filename:
            plotter.loadHistFromChain(hist, 
                glob.glob(filename), 
                path_to_tree, 
                branch_name, 
                cut_string,
                max_entries,
                append
            )
        else:
            print "Invalid file! %s does not exist" % filename
            exit(1)
def getChain(filelist, path_to_tree):
    filelist = glob.glob(filelist)
    tree = ROOT.TChain(path_to_tree)
    for file_name in filelist:
        tree.Add(file_name)
    return tree
def getScaleFactors(hist_no_cut, analysis_tree, file_name):
    noCutWeightsSum = hist_no_cut.Integral()
    metadata = helper.getChain(filename,
            analysis_tree.replace("Ntuple", "MetaData")
    )
    
    totals = { "inputXSection" : 0,
        "fidXSection" : 0,
        "nPass" : 0,
        "fidSumWeights" : 0
    }
    
    num_files = 0
    for row in metadata:
        num_files += 1
        for key, in totals:
            counters[key] += row.getattr(key)
    counters["inputXSection"] /= num_files
    counters["fidXSection"] /= num_files
    #print "The input x section was %f" % xSec
    
    return (counters["inputXSection"], counters["fidXSection"])
    fid_scale_factor = fidXSec/noCutWeightsSum
    input_scale_factor = fidXSec/noCutWeightsSum
    return (
    
def scaleHistByLumi(, lumi):
    print "%i initial events, %i selected events" % (numEvents, hist.GetEntries())
    print "The new fiducial cross section is %f" % new_fidXSec 
    print "Scaled by %s" % scale_factor
    hist.Sumw2()
    hist.Scale(scale_factor*lumi)
