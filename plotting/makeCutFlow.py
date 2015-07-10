
def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_file", type=str, required=True,
                        help="Name of file to be created (type pdf/png etc.)")
    parser.add_argument("--no_flow", action="store_true",
                        help="Name of file to be created (type pdf/png etc.)")
    parser.add_argument("-s", "--scale", type=str, default="xsec",
                        help="Method for scalling hists")
    parser.add_argument("-f", "--file_to_plot", type=str, required=True,
                        default="", help="Files to make plots from, "
                        "separated by a comma (match name in file_info.json)")
    return parser.parse_args()
def main():
    cuts = [{"Z mass" : selection.getZMassCutString() },
           {"lepton pt cuts" : selection.getPtCutString() },
           {"lepton eta cuts" : selection.getEtaCutString() }
    ]
    cut_flow = ROOT.TH1F(

    for cut_name, cut_value in cuts.iteritems():
        if cut_string != "":
            cut_string += " && "
        cut_string += cut_value
        for name, entry in file_info.iteritems():
            if entry["name"] not in args.file_to_plot.strip():
                continue
            temphist = ROOT.TH1F("temp", "temp", 1000, -1000, 1000)

        root_file = ROOT.TFile(entry["filename"])
        if not root_file:
            print 'Failed to open %s' % root_file
            exit(0)
        num_passed = plotter.loadHistFromTree(hist, 
            root_file, 
            "analyzeWZ/Ntuple",
            "zMass",
            cut_string
        )
