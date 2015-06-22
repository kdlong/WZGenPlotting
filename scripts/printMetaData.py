#!/bin/env python
import ROOT
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input_file', type=str,
                    help="Input root file.")
args = parser.parse_args()

root_file = ROOT.TFile(args.input_file)
tree = root_file.Get("analyzeWZ/MetaData")

for row in tree:
    print "This initial cross section was %s" % row.inputXSection
    print "This fiducial cross section was %s" % row.fidXSection
    print "Initial number of events is %s" % row.nProcessedEvents
    print "Selected number of events is %s" % row.nPass
