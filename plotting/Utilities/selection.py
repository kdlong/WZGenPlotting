import itertools

def getEtaCutString(numLeptons):
    cut_string = ""
    for i in range(1, numLeptons+1):
        if i != 1:
            cut_string += " && "
        cut_string +=  "(abs(l%ipdgId) == 11 ? abs(l%iEta) < 2.5 : abs(l%iEta) < 2.5)" % (i, i, i)
    return cut_string
def getPtCutString(pt_cuts, analysis):
    if analysis == "ZZvary":
        return " && ".join(["l1Pt > 20 && l2Pt > 10"]+["(abs(l%ipdgId) == 11 ? (l%iPt > 7) : (l%iPt > 5))" % (i, i, i) for i in [3, 4]])
    elif "WZ" in analysis and "vary" in analysis:
        return "l1Pt > 20 && l2Pt > 20 && (abs(l3motherId) == 24 ? l3Pt > 20 : l3Pt > 10)"
    cut_string = ""
    for i, cut in enumerate(pt_cuts):
        if i != 0:
            cut_string += " && "
        cut_string += "l%iPt > %s " % ((i +1), str(cut))
    return cut_string
def getZMassCutString(analysis, requireTrue):
    if analysis == "WZ":
        if requireTrue:
            return "((Z1mass < 120 && Z1mass > 60 && Z1isTrueZ) || " \
                   "(Z2mass < 120 && Z2mass > 60 && Z2isTrueZ))"
        else:
            return "(Z1mass < 120 && Z2mass > 60"
    elif analysis == "ZZ":
        if requireTrue:
            final_cut_string =[]
            for i, j in itertools.combinations([1,2,3,4], 2):
                cut_string = ["(Z%iisTrueZ && Z%iisTrueZ" % (i, j)]
                cut_string += ["(Z%imass > 60 && Z%imass < 120)" % (i, i)]
                cut_string += [ "(Z%imass > 60 && Z%imass < 120))" % (j, j)]
                final_cut_string += [" && ".join(cut_string)]
            return "(" + " || ".join(final_cut_string) + ")"
        else:
            return "((Z1mass < 120 && Z1mass > 60 && Z1isUnique) && " \
                 "(Z2mass < 120 && Z2mass > 60 && Z2isUnique))"
    elif analysis == "WZ8TeV":
        return "Z1mass < 111.11 && Z1mass > 71.11"
def getChannelEEMCutString():
    cut_string = "((abs(l1pdgId) == 11 && abs(l2pdgId) == 11 && abs(l3pdgId) == 13)" \
        " || (abs(l1pdgId) == 11 && abs(l2pdgId) == 13 && abs(l3pdgId) == 11)" \
        " || (abs(l1pdgId) == 13 && abs(l2pdgId) == 11 && abs(l3pdgId) == 11))"
    return cut_string
def getChannelEMMCutString():
    cut_string = "((abs(l1pdgId) == 13 && abs(l2pdgId) == 13 && abs(l3pdgId) == 11)" \
        " || (abs(l1pdgId) == 13 && abs(l2pdgId) == 11 && abs(l3pdgId) == 13)" \
        " || (abs(l1pdgId) == 11 && abs(l2pdgId) == 13 && abs(l3pdgId) == 13))"
    return cut_string
def getChannelEEECutString():
    cut_string = "(abs(l1pdgId) == 11 && abs(l2pdgId) == 11 && abs(l3pdgId) == 11)"
    return cut_string
def getChannelMMMCutString():
    cut_string = "(abs(l1pdgId) == 13 && abs(l2pdgId) == 13 && abs(l3pdgId) == 13)"
    return cut_string
def getChannelEEEECutString():
    cut_string = "(abs(l1pdgId) == 11 && abs(l2pdgId) == 11 && abs(l3pdgId) == 11 && abs(l4pdgId) == 11)"
    return cut_string
def getChannelMMMMCutString():
    cut_string = "(abs(l1pdgId) == 13 && abs(l2pdgId) == 13 && abs(l3pdgId) == 13 && abs(l4pdgId) == 13)"
    return cut_string
def getChannelEEMMCutString():
    cut_string = "((abs(l1pdgId) == 11 && abs(l2pdgId) == 11 && abs(l3pdgId) == 13 && abs(l4pdgId) == 13)" \
        " || (abs(l1pdgId) == 13 && abs(l2pdgId) == 13 && abs(l3pdgId) == 11 && abs(l4pdgId) == 11)" \
        " || (abs(l1pdgId) == 13 && abs(l2pdgId) == 11 && abs(l3pdgId) == 13 && abs(l4pdgId) == 11)" \
        " || (abs(l1pdgId) == 13 && abs(l2pdgId) == 11 && abs(l3pdgId) == 11 && abs(l4pdgId) == 13)" \
        " || (abs(l1pdgId) == 11 && abs(l2pdgId) == 13 && abs(l3pdgId) == 13 && abs(l4pdgId) == 11)" \
        " || (abs(l1pdgId) == 11 && abs(l2pdgId) == 13 && abs(l3pdgId) == 11 && abs(l4pdgId) == 13))"
    return cut_string
def getFiducialCutString(analysis, trueZ):
    if "WZ" in analysis:
        numLeptons = 3
        pt_cuts = [20, 10, 10]
    else:
        numLeptons = 4
        pt_cuts = [20, 10, 10, 10]
    return " && ".join([getEtaCutString(numLeptons), 
        getPtCutString(pt_cuts, analysis + ("vary" if "WZ" in analysis else "")), 
        getZMassCutString(analysis, trueZ)])
