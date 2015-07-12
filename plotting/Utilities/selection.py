def getEtaCutString(numLeptons):
    cut_string = ""
    for i in range(1, numLeptons+1):
        if i != 1:
            cut_string += " && "
        cut_string +=  "(abs(l%ipdgId) == 11 ? abs(l%iEta) < 2.5 : abs(l%iEta) < 2.5)" % (i, i, i)
    return cut_string
def getPtCutString(pt_cuts):
    cut_string = ""
    for i, cut in enumerate(pt_cuts):
        if i != 0:
            cut_string += " && "
        cut_string += "l%iPt > %s " % ((i +1), str(cut))
    return cut_string
def getZMassCutString(numZ):
    if numZ == 1:
        return "(zMass < 120 && zMass > 60)"
    cut_string = ""
    for i in range(1, numZ+1):
        if i != 0:
            cut_string += " && (z%iMass < 120 && z%iMass > 60)" % (i,i)
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
def getFiducialCutString(analysis):
    if analysis is "WZ":
        numLeptons = 3
        pt_cuts = [20, 10, 10]
        numZs = 1
    else:
        numLeptons = 4
        pt_cuts = [20, 10, 10]
        numZs = 2
    cut_string = getEtaCutString(numLeptons)
    cut_string += " && " + getPtCutString(pt_cuts)
    cut_string += " && " + getZMassCutString(numZs)
    return cut_string
