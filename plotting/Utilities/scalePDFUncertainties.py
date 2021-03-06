import math
import ROOT
from collections import OrderedDict
import numpy

def getVariations(weight_ids, weight_sums):
    values = {"1001" : OrderedDict(), 
            "2001" : OrderedDict(), 
            "3001" : OrderedDict(),
            "4001" : OrderedDict()
    }
    if len(weight_ids) != len(weight_sums):
        print "Should have equal number of weights and IDs!!!"
        exit(1)
    if float(weight_ids[0]) > 10:
        for weight in zip(weight_ids, weight_sums):
            label = ''.join([weight[0][0], "001"]) 
            values[label][weight[0]] = weight[1]
    else:
        # Hackity hack hack for MadGraph LO samples
        for i,weight in enumerate(zip(weight_ids, weight_sums)):
            entry = 1
            weight_id = str(1000+i+1)
            if i > 8:
                entry = 2
                weight_id = str(2000+i-8)
            label = ''.join([str(entry), "001"]) 
            values[label][weight_id] = weight[1]
            if i > 109:
                break
    return values

def getFiducialWeightSums(proof_file_path, cut_string):
    proof = ROOT.gProof
    proof.Load("sumWeights.C+")
    sumWeights = ROOT.sumWeights()
    proof.Process(proof_file_path, sumWeights, cut_string)
    summedWeightsHist = sumWeights.GetOutputList().FindObject('summedWeights')
    canvas = ROOT.TCanvas("canvas", "canvas", 600, 800)
    summedWeightsHist.Draw("hist")
    sums = []
    for i in xrange(1, summedWeightsHist.GetSize() + 1):
        sums.append(summedWeightsHist.GetBinContent(i))
    sums = sums[:sums.index(0.0)]
    return sums
# The largest and smallest values for variations of uR and uF 0.5, 1, 2
# times their central values are as the scale uncertainty.
# Assymetric variations (e.g. uF = 0.5, uR = 2) are excluded
def getScaleUncertainty(values):
    scale_info = {}
    central = values["1001"]["1001"]
    exclude = ["1006", "1008"]
    scales = [value for key, value in values["1001"].iteritems() if key not in exclude]
    scale_info['down'] = (1-min(scales)/central)*100
    scale_info['up'] = (max(scales)/central - 1)*100
    return scale_info
# Compute alpha_s variation uncertainties, using alpha_s = 0.116 and 0.120, which
# are stored as weight 2101 and 2102 in CMS samples, according to equation 27 in
# PDF4LHC paper: http://arxiv.org/pdf/1510.03865v1.pdf
def getAlphaSUncertainty(values):
    central = values["1001"]["1001"]
    return abs(values["2001"]["2101"] - values["2001"]["2102"])*100/(2*central)
# Compute Gaussian PDF uncertainties, appropriate for NNPDF
def getNNPDFUncertainty(values):
    pdf_unc = {}
    central = values["1001"]["1001"]
    # These are alpha_s variations
    exclude = ["2102", "2101"]
    variations = [value for key, value in values["2001"].iteritems() if key not in exclude]
    variance = 0
    for xsec in variations:
        variance += (xsec - central)*(xsec - central)
        num = len(variations) - 1
    return math.sqrt(variance/(num))/central*100
# Combine PDF fit and alpha_s uncertainties according to PDF4LHC recommendation.
# Equation 30 in http://arxiv.org/pdf/1510.03865v1.pdf, with r = 1.5
# (alpha_s uncertainty is +- 0.0015, and we use 0.119 and 0.117 PDF sets)
def getFullPDFUncertainty(values):
    pdf_unc = getNNPDFUncertainty(values)
    alpha_s_unc = getAlphaSUncertainty(values)
    # Taken to give the +- 0.00015 variation
    r = 1.5
    return math.sqrt(pdf_unc*pdf_unc + r*r*alpha_s_unc*alpha_s_unc)
