#include <iostream>
#include <vector>
#include "TSystem.h"
#include "TClonesArray.h"
#include <algorithm>

#include "/data/kelong/MadGraph-CMS/MG5_aMC_v2_2_2/ExRootAnalysis//ExRootAnalysis/ExRootTreeReader.h"
#include "/data/kelong/MadGraph-CMS/MG5_aMC_v2_2_2/ExRootAnalysis//ExRootAnalysis/ExRootTreeWriter.h"
#include "/data/kelong/MadGraph-CMS/MG5_aMC_v2_2_2/ExRootAnalysis//ExRootAnalysis/ExRootTreeBranch.h"
#include "/data/kelong/MadGraph-CMS/MG5_aMC_v2_2_2/ExRootAnalysis//ExRootAnalysis/ExRootResult.h"
#include "/data/kelong/MadGraph-CMS/MG5_aMC_v2_2_2/ExRootAnalysis//ExRootAnalysis/ExRootUtilities.h"
#include "/data/kelong/MadGraph-CMS/MG5_aMC_v2_2_2/ExRootAnalysis//ExRootAnalysis/ExRootClasses.h"

//gSystem->Load("/data/kelong/MadGraph-CMS/MG5_aMC_v2_2_2/ExRootAnalysis/libExRootAnalysis.so");

void uncertaintyFromExRoot(const char *inputFile) {
    TChain *chain = new TChain("LHEF");
    chain->Add(inputFile);

    ExRootTreeReader *treeReader = new ExRootTreeReader(chain);
    TClonesArray *branchWeight = treeReader->UseBranch("Rwgt");
    TRootWeight *rwgt; 
   
    std::vector<float> weight_sums(112, 0.0);
    for(int i = 0; i < treeReader->GetEntries(); i++) {
        // Load selected branches with data from specified event
        treeReader->ReadEntry(i);
        for (int j = 0; j < branchWeight->LastIndex(); j++) {
            rwgt = dynamic_cast<TRootWeight*>(branchWeight->At(j));
            weight_sums[j] += rwgt->Weight;
            std::cout << " " << j;
        }
    }
    for (const auto& sum : weight_sums)
        std::cout << sum << std::endl;
}       
