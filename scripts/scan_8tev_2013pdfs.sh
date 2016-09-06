#!/bin/bash
zpt=0
count=20
max_value=140
while [ $zpt -lt $max_value ]
do
    python cutAndCount.py -f wz8tev-pwg-13pdfs -u -a WZ -d "zMass8TeV" \
        -m "Z1Pt > $zpt && Z1Pt < $[ $zpt + $count ]" \
        --print_scale \
        --print_pdf \
        > ~/www/DibosonCrossSections/WZ8TeV/2013PDFs/WZ8TeV_eem_Zwindow_ZPt_${zpt}.out
    python cutAndCount.py -f wz8tev-pwg-13pdfs -u -a WZ -d "WZ8TeV" \
        -m "Z1Pt > $zpt && Z1Pt < $[ $zpt + $count ] && NuPt > 30" \
        --print_scale \
        --print_pdf \
        > ~/www/DibosonCrossSections/WZ8TeV/2013PDFs/WZ8TeV_eem_fiducial_ZPt_${zpt}.out
    zpt=$[$zpt + $count]
done
exit
count=60
python cutAndCount.py -f wz8tev-pwg-13pdfs -u -a WZ -d "zMass8TeV" \
    -m "Z1Pt > $zpt && Z1Pt < $[ $zpt + $count ]" \
    --print_scale \
    --print_pdf \
    > ~/www/DibosonCrossSections/WZ8TeV/2013PDFs/WZ8TeV_eem_Zwindow_ZPt_${zpt}.out
python cutAndCount.py -f wz8tev-pwg-13pdfs -u -a WZ -d "WZ8TeV" \
    -m "Z1Pt > $zpt && Z1Pt < $[ $zpt + $count ] && NuPt > 30  " \
    --print_scale \
    --print_pdf \
    > ~/www/DibosonCrossSections/WZ8TeV/2013PDFs/WZ8TeV_eem_fiducial_ZPt_${zpt}.out
zpt=$[$zpt + $count]
count=100
python cutAndCount.py -f wz8tev-pwg-13pdfs -u -a WZ -d "zMass8TeV" \
    -m "Z1Pt > $zpt && Z1Pt < $[ $zpt + $count ]" \
    --print_scale \
    --print_pdf \
    > ~/www/DibosonCrossSections/WZ8TeV/2013PDFs/WZ8TeV_eem_Zwindow_ZPt_${zpt}.out
python cutAndCount.py -f wz8tev-pwg-13pdfs -u -a WZ -d "WZ8TeV" \
    -m "Z1Pt > $zpt && Z1Pt < $[ $zpt + $count ] && NuPt > 30" \
    --print_scale \
    --print_pdf \
    > ~/www/DibosonCrossSections/WZ8TeV/2013PDFs/WZ8TeV_eem_fiducial_ZPt_${zpt}.out
zpt=300
python cutAndCount.py -f wz8tev-pwg-13pdfs -u -a WZ -d "zMass8TeV" \
    -m "Z1Pt > $zpt" \
    --print_scale \
    --print_pdf \
    > ~/www/DibosonCrossSections/WZ8TeV/2013PDFs/WZ8TeV_eem_Zwindow_ZPt_${zpt}.out
python cutAndCount.py -f wz8tev-pwg-13pdfs -u -a WZ -d "WZ8TeV" \
    -m "Z1Pt > $zpt && NuPt > 30 && NuPt > 30" \
    --print_scale \
    --print_pdf \
    > ~/www/DibosonCrossSections/WZ8TeV/2013PDFs/WZ8TeV_eem_fiducial_ZPt_${zpt}.out
