import ROOT
import WeightInfo

class WeightedHistProducer(object):
    def __init__(self, chain, weight_info, weight_branch):
        self.histChain = chain 
        self.weight_info = weight_info 
        self.weight_branch = weight_branch
        self.event_weight = self.weight_info.getCrossSection()/self.weight_info.getSumOfWeights()
        self.lumi = 1/self.event_weight
    def setLumi(self, lumi):
        self.lumi = lumi
    def loadHist(self, hist, branch_name, cut_string, max_entries, append=False):
        hist.GetDirectory().cd() 
        hist_name = "".join(["+ " if append else "", hist.GetName()])
        print "name is %s" % hist_name
        old_num = hist.GetEntries()
        num = self.histChain.Draw(branch_name + ">>" + hist_name, 
                cut_string,
                "",
                max_entries if max_entries > 0 else 1000000000)
        print "Draw Comand is %s" % branch_name + ">>" + hist_name
        print "With cut string %s" % cut_string
        if append:
            if num < old_num:
                print "Failed to append to hist"
        print hist.GetEntries()
        return num
    def produce(self, hist, branch_name, cut_string="", max_entries=-1, append=False): 
        hist_no_cut = hist.Clone("hist_no_cut")
        self.loadHist(hist_no_cut,
                branch_name,
                self.weight_branch,
                max_entries
        )
        init_sum_weights = hist_no_cut.Integral()
        self.loadHist(hist,
            branch_name,
            ''.join([self.weight_branch, "*(" + cut_string + ")" if cut_string != "" else ""]),
            max_entries
        )
        fid_sum_weights = hist.Integral()
        scale_fac = fid_sum_weights/init_sum_weights
        hist.Scale(self.event_weight*scale_fac*self.lumi)
        del hist_no_cut
# For testing
def main():
    root_file = ROOT.TFile("/afs/cern.ch/user/k/kelong/work/DibosonMCAnalysis/ZZTo4LNu0j_5f_NLO_FXFX/MG5aMCatNLO_ZZTo4LNu0j_muMass_pythia8_TuneCUETP8M1_Ntuple.root")
    metaTree = root_file.Get("analyzeZZ/MetaData")
    weight_info = WeightInfo.WeightInfoProducer(metaTree, "fidXSection", "fidSumWeights").produce()

    ntuple =root_file.Get("analyzeZZ/Ntuple")
    histProducer = WeightedHistProducer(ntuple, weight_info, "weight")  
    
    canvas = ROOT.TCanvas("canvas", "canvas", 600, 800)
    hist = ROOT.TH1F("hist", "hist", 60, 60, 120)
    histProducer.produce(hist, "Z1mass", "", 1000)
    hist.Draw("hist")
    canvas.Print("test1.pdf")
    
    histProducer.produce(hist, "Z1mass", "Z1mass < 120 && Z1mass > 60")
    hist.Draw("hist")
    canvas.Print("test2.pdf")

    histProducer.produce(hist, "Z1mass", "Z1mass < 100")
    hist.Draw("hist")
    canvas.Print("test3.pdf")
if __name__ == "__main__":
    main()
