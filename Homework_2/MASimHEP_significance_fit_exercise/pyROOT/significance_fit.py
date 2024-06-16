# PyROOT: https://root.cern/manual/python/
# execution:
# python significance_fit.py -b


# 𝐻→𝑊𝑊  search using the ATLAS Open Data
# ---------------------------------------------------------------------
# In this exercise, you are given a file containing an analysis TTree with selected event data from the search 
# for a Higgs boson decaying to WW pairs, where both W bosons decay leptonically.

# The TTree contains several observables, such as:

#  mLL: invariant mass of the dilepton pair
#  ptLL: transverse momentum of the dilepton pair
#  dPhi_LL: angular separation in azimuthal angle between the two charged leptons of the event
#  dPhiLLmet: angular separation in azimuthal angle between missing transverse energy and the dilepton pair
#  MET: missing transverse energy
#  mT: transverse mass (i.e. invariant mass calculated with the transverse components of missing ET and 
#  the two leptons)
#  goodjet_n: number of jets in the event (after quality criteria)
#  goodbjet_n: number of b jets in the event (after quality criteria)
#  For each of the leptons: transverse momentum pT, eta (pseudorapidity), energy E, azimuthal angle phi and charge
#  process: label indicating the kind of background taken into account
#  label: 0 for background, 1 for signal (valid only in MC simulation, for real data is -1)
#  weight: correction factors to take into account differences in reconstruction between data and MC simulation 
#  scale_weight: total event weight (including the MC correction weight above) used to normalise each event to 
#  its physical expectation, such that the sum of scale_weight yields the total number of expected events for the process


# The goals of this exercise are:

## 1) Make histograms of a few variables for the signal and background in the same plot (pTLL, dPhiLLmet, dPhi_LL, MET, mT). 
#     (Tip: you may first explore the TTree using the TBrowser to check the limits of the distributions)
## 2) Choose two variables for the signal selection optimisation. Justify your choice. 
## 3) Optimize the signal selection criteria using these two variables.
## 4) Draw the mT (transverse invariant mass of the WW pair) distribution after applying your selection conditions for the signal and the backgrounds with data and MC.
## 5) Build a test-statistics for signal discovery and use the data to perform a maximum-likelihood fit 
# to compute the observed and signal strength in the data sample, using mT as observable. 
# Based on the results of the test statistics, which one of the two hypotheses is more likely (background only or signal+background)? 
# Explain the reasoning behind your answer.

import ROOT
import math

print('Hello!')

# Open simulation file with TTree located in the folder: ../data/
MCfile = ROOT.TFile("../data/MC.root","READ")
MCtree = MCfile.Get("hWWAna")

# Inspect TTree
#MCtree.Print()

## Example on how to make histograms
# Get signal and bkg histogram
histname = "mLL"
sighist = ROOT.TH1F(histname+"sig","",9,0.,60.)
MCtree.Draw(histname+">>"+histname+"sig","scale_weight*(label==1)")
bkghist = ROOT.TH1F(histname+"bkg","",9,0.,60.)
MCtree.Draw(histname+">>"+histname+"bkg","scale_weight*(label==0)")

print('\n\n++ Statistics before my optimised selection')
print(f'    signal histogram entries {sighist.GetEntries():.0f} expected events {sighist.Integral():.1f}')
print(f'background histogram entries {bkghist.GetEntries():.0f} expected events {bkghist.Integral():.1f}')
print(f'Total S/sqrt(S+B) {sighist.Integral()/math.sqrt(sighist.Integral()+bkghist.Integral()):.2f}')

# Plot signal vs background histograms
c = ROOT.TCanvas()

# Aesthetics and legend
sighist.SetLineColor(2) #red
sighist.SetLineWidth(2)
bkghist.SetLineColor(8) # green
bkghist.SetLineWidth(2)
bkghist.GetXaxis().SetTitle("mLL [GeV]")

legend = ROOT.TLegend()
bkghist.Draw("hist")
bkghist.SetMinimum(0)
sighist.Draw("histsame")
legend.AddEntry(sighist, "HWW signal")
legend.AddEntry(bkghist, "background")
legend.Draw()
c.Print(f"{histname}.png")


## Example on how to obtain a histogram after the selection cuts
sighistSEL = ROOT.TH1F(histname+"sigSEL","",10,0.,60.)
MCtree.Draw(histname+">>mLLsigSEL","scale_weight*(label==1 && MET<80 && dPhiLLmet>1.8)")
bkghistSEL = ROOT.TH1F(histname+"bkgSEL","",10,0.,60.)
MCtree.Draw(histname+">>mLLbkgSEL","scale_weight*(label==0 && MET<80 && dPhiLLmet>1.8)")

print('\n\n++ Statistics after my optimised selection')
print(f'    signal histogram entries {sighistSEL.GetEntries():.0f} expected events {sighistSEL.Integral():.1f}')
print(f'background histogram entries {bkghistSEL.GetEntries():.0f} expected events {bkghistSEL.Integral():.1f}')
print(f'Total S/sqrt(S+B) improved from {sighist.Integral()/math.sqrt(sighist.Integral()+bkghist.Integral()):.2f} to {sighistSEL.Integral()/math.sqrt(sighistSEL.Integral()+bkghistSEL.Integral()):.2f}')


# Use real data to perform the discovery fit and the test statistics
datafile = ROOT.TFile("../data/data.root","READ")
datatree = datafile.Get("hWWAna")
datahist = ROOT.TH1F(histname+"data","",9,0.,60.)
datatree.Draw(histname+">>"+histname+"data","")


# Close files in the end
MCfile.Close()
datafile.Close()