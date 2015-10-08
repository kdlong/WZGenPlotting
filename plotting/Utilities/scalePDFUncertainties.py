import math
import ROOT
from collections import OrderedDict

def getVariations(weight_ids, weight_sums):
    values = OrderedDict()
    if len(weight_ids) != len(weight_sums):
        print "Should have equal number of weights and IDs!!!"
        exit(1)
    for weight in zip(weight_ids, weight_sums):
        label = ''.join([weight[0][0], "001"]) 
        if label not in values:
            values.update( { label : {}})
        values[label].update({weight[0] : weight[1]})
    return values

def getFiducialWeightSums(proof_file_path, cut_string):
    proof = ROOT.gProof
    proof.Load("sumWeights.C+")
    sumWeights = ROOT.sumWeights()
    proof.Process(proof_file_path, sumWeights, cut_string)
    summedWeightsHist = sumWeights.GetOutputList().FindObject('summedWeights')
    canvas = ROOT.TCanvas("canvas", "canvas", 600, 800)
    summedWeightsHist.Draw("hist")
    canvas.Print("test.pdf")
    sums = []
    for i in xrange(1, summedWeightsHist.GetSize() + 1):
        sums.append(summedWeightsHist.GetBinContent(i))
    sums = sums[:sums.index(0.0)]
    return sums
def getScaleUncertainty(values):
    scale_info = {}
    central = values["1001"]["1001"]
    scale_info['down'] = (1-min(values["1001"].values())/central)*100
    scale_info['up'] = (max(values["1001"].values())/central - 1)*100
    return scale_info
def getPDFUncertainty(values):
    pdf_unc = {}
    central = values["1001"]["1001"]
    print central
    for unc_set in values:
        if "1001" in unc_set:
            continue
        variance = 0
        for pdf_id, xsec in values[unc_set].iteritems():
            variance += (xsec - central)*(xsec - central)
            num = len(values[unc_set]) - 1
        pdf_unc[unc_set] = math.sqrt(variance/(num))/central*100
    return pdf_unc
