import ROOT
import math
import numpy as np
from ROOT.Math import poisson_pdf

# QUESTION 1: Make histograms of a few variables for the signal and background in the same plot (pTLL, dPhiLLmet, dPhi_LL, MET, mT). 
# I used the TBrowser function, as suggested, so that I could establish the bin limits.

print("QUESTION 1")


MCfile = ROOT.TFile("../data/MC.root","READ")
MCtree = MCfile.Get("hWWAna")

# Define variables, their limits and number of bins (used TBrowser). Division of canvas gave an extra space, hence used another variable.

variables =  ["ptLL","dPhiLLmet","dPhi_LL","MET","mt","goodbjet_n"]
limits = [[0.,200.],[1.2,3.2],[0.,2.],[0.,300.],[0.,300.],[0.,2.]]
bins = [200,200,200,300,300,2]

canvas = ROOT.TCanvas()
canvas.Divide(3,2)

sighist = []
bkghist = []
legend = []

for i in range(len(variables)):
  canvas.cd(i+1)

  sighist.append(ROOT.TH1F(variables[i] + "_sig", "", bins[i], limits[i][0], limits[i][1]))
  bkghist.append(ROOT.TH1F(variables[i] + "_bkg", "", bins[i], limits[i][0], limits[i][1]))

  MCtree.Draw(f"{variables[i]} >> {variables[i]}_sig", "scale_weight * (label == 1)")
  MCtree.Draw(f"{variables[i]} >> {variables[i]}_bkg", "scale_weight * (label == 0)")

  
  sighist[i].SetLineColor(ROOT.kRed)
  sighist[i].SetStats(0)
  bkghist[i].SetStats(0)
  bkghist[i].SetLineColor(ROOT.kBlue)
  bkghist[i].GetXaxis().SetTitle(f"{variables[i]} [GeV]")

  legend.append(ROOT.TLegend(0.7, 0.3, 0.9, 0.4))
  legend[i].AddEntry(sighist[i], "HWW signal")
  legend[i].AddEntry(bkghist[i], "Background")

  bkghist[i].Draw("hist")
  sighist[i].Draw("histsame")
  legend[i].Draw()

canvas.Print("../Plots_Notes_HW_100306/MChistsWithStats.pdf")
canvas.Clear()

# Question 2: Choose two variables for the signal selection optimisation. Justify your choice. 

print("\n\nQUESTION 2") 

print("\n The two variables used were ptLL and MET. Signal selection optimisation intends to discriminate your signal from the different backgrounds.")
print("As such, we intend to apply cuts in variables to optimise the signal yield but we do not want to loose any signal. It is a compromise between these two.")
print("As plotted in the previous exercise, we observe for these two variables clear signal peaks, which, as a consequence of what was stated earlier, leads to this choice.")


# Question 3: 3) Optimize the signal selection criteria using these two variables.

print("\n\nQUESTION 3") 

# In the previous question, we chose two variables for the signal selection optimisation. In this one, we shall choose the cuts to be used by applying cuts and calculating Z,
# choosing the maximum. We perform this left to right and right to left to have an interval. 

def significance(sig,bkg):
  if bkg == 0:
    return 0
  else:
    value = math.sqrt(2*(sig+bkg)*math.log(1+sig/bkg)-2*sig)
  return value

#The first position of cuts gives the left-right cuts, wheras the second gives the right-left cuts. The first position is for ptLL and the second for MET.
cuts = [[0.,0.],[0.,0.]]

# Cut starting from left to right.

canvas.Divide(2,1)

indexes = [0,3]

clones_sig_hist = [sighist[0].Clone(),sighist[3].Clone()]

for i in range(len(clones_sig_hist)):
  S = 0.
  B = 0.
  for j in range(1,clones_sig_hist[i].GetNbinsX()+1):
    S = S +  sighist[indexes[i]].GetBinContent(j)
    B = B + bkghist[indexes[i]].GetBinContent(j)
    clones_sig_hist[i].SetBinContent(j,significance(S,B))
  canvas.cd(i+1)
  cuts[0][i] = clones_sig_hist[i].GetXaxis().GetBinCenter(clones_sig_hist[i].GetMaximumBin())
  clones_sig_hist[i].SetStats(0)
  clones_sig_hist[i].GetXaxis().SetTitle(f"{variables[indexes[i]]} [GeV]")
  clones_sig_hist[i].GetYaxis().SetTitle("Significance Left-Right")
  clones_sig_hist[i].Draw("histsame")
canvas.Print("../Plots_Notes_HW_100306/Significance_LR.pdf")
canvas.Clear()

# Cut starting from right to left

canvas.Divide(2,1)

clones_sig_hist = [sighist[0].Clone(),sighist[3].Clone()]

for i in range(len(clones_sig_hist)):
  S = 0.
  B = 0.
  for j in range(1,clones_sig_hist[i].GetNbinsX()+1):
    S = S +  sighist[indexes[i]].GetBinContent(clones_sig_hist[i].GetNbinsX()+1 - j)
    B = B + bkghist[indexes[i]].GetBinContent(clones_sig_hist[i].GetNbinsX()+1 - j)
    clones_sig_hist[i].SetBinContent(clones_sig_hist[i].GetNbinsX()+1 - j,significance(S,B))
  canvas.cd(i+1)
  cuts[1][i] = clones_sig_hist[i].GetXaxis().GetBinCenter(clones_sig_hist[i].GetMaximumBin())
  clones_sig_hist[i].SetStats(0)
  clones_sig_hist[i].GetXaxis().SetTitle(f"{variables[indexes[i]]} [GeV]")
  clones_sig_hist[i].GetYaxis().SetTitle("Significance Right-Left")
  clones_sig_hist[i].Draw("histsame")
canvas.Print("../Plots_Notes_HW_100306/Significance_RL.pdf")
canvas.Clear()

print("\nFor the ptLL variable, the cut is at {:.2f} GeV.".format(cuts[0][0]))
print("\nFor the MET variable, the cut is at {:.2f} GeV.".format(cuts[0][1]))

# Question 4:  Draw the mT (transverse invariant mass of the WW pair) distribution after applying your selection conditions for the signal and the backgrounds with data and MC.
# Since the right-left cut gave the last bin, I did not take it into consideration, only imposing a cut using the left-right, as explained earlier.

print("\n\nQUESTION 4") 

histname = "mt"

sighistSEL = ROOT.TH1F(histname+"sigSEL","",bins[4],limits[4][0],limits[4][1])
MCtree.Draw(histname+">>mtsigSEL",f"scale_weight * (label==1 && ptLL< {cuts[0][0]} && MET<{cuts[0][1]})")
bkghistSEL = ROOT.TH1F(histname+"bkgSEL","",bins[4],limits[4][0],limits[4][1])
MCtree.Draw(histname+">>mtbkgSEL",f"scale_weight * (label==0 && ptLL< {cuts[0][0]} && MET<{cuts[0][1]})")
print('\n\n++ Statistics after my optimised selection')
print(f'Signal histogram entries {sighistSEL.GetEntries():.0f} expected events {sighistSEL.Integral():.1f}')
print(f'Background histogram entries {bkghistSEL.GetEntries():.0f} expected events {bkghistSEL.Integral():.1f}')
print(f'Total S/sqrt(S+B) improved from {sighist[4].Integral()/math.sqrt(sighist[4].Integral()+bkghist[4].Integral()):.2f} to {sighistSEL.Integral()/math.sqrt(sighistSEL.Integral()+bkghistSEL.Integral()):.2f}')



sighistSEL.SetLineColor(2) 
sighistSEL.SetLineWidth(2)
bkghistSEL.SetLineColor(4) 
bkghistSEL.SetLineWidth(2)
bkghistSEL.GetXaxis().SetTitle("mt [GeV]")
bkghistSEL.SetStats(0)
sighistSEL.SetStats(0)

legend2 = ROOT.TLegend(0.7, 0.3, 0.9, 0.4)
bkghistSEL.Draw("hist")
bkghistSEL.SetMinimum(0)

sighistSEL.Draw("histsame")
legend2.AddEntry(sighistSEL, "HWW signal")
legend2.AddEntry(bkghistSEL, "background")
legend2.Draw()
canvas.Print(f"../Plots_Notes_HW_100306/Expected{histname}.pdf")
canvas.Clear()

# Question 5: Build a test-statistics for signal discovery and use the data to perform a maximum-likelihood fit 
# to compute the observed and signal strength in the data sample, using mT as observable. 
# Based on the results of the test statistics, which one of the two hypotheses is more likely (background only or signal+background)? 
# Explain the reasoning behind your answer.

print("\n\nQUESTION 5") 

datafile = ROOT.TFile("../data/data.root","READ")
datatree = datafile.Get("hWWAna")
datahist = ROOT.TH1F(histname+"data","",bins[4],limits[4][0],limits[4][1])
datatree.Draw(histname+">>"+histname+"data","")

# Plot of measured transverse mass (not requested)

datahist.GetXaxis().SetTitle("mt [GeV]")
datahist.SetStats(0)
datahist.SetTitle("Measured Transverse Mass")
canvas.Print("../Plots_Notes_HW_100306/mt_measured.pdf")
canvas.Clear()

# Maximum-likelihood estimate for mu can be determined using the log-likelihood:

def log_likelihood(mu, signal_exp, bkg_exp, data):
  likelihood_result = np.zeros(signal_exp.GetNbinsX())
  for i in range(signal_exp.GetNbinsX()):
    expected = mu*signal_exp.GetBinContent(i) + bkg_exp.GetBinContent(i)
    datavalue = data.GetBinContent(i)
    if expected != 0:
      likelihood_result[i] = math.log(poisson_pdf(int(datavalue),expected)) #Caution: this is defined in https://root.cern/doc/master/group__PdfFunc.html and we need to used integers
    else:
      likelihood_result[i] = 0
  return np.sum(likelihood_result)

# Plot log-likelihood for mu values between 0 and 10 with a step of 0.01, which gives 

log_likelihood_plot = ROOT.TH1F("log_likelihood","",1000,0,10)

# In order to reach the value 10, I have to add 1. Recall that i starts in 0.
for i in range(10001):
  mu = 0.01*i
  log_mu = log_likelihood(mu,sighistSEL,bkghistSEL,datahist)
  log_likelihood_plot.SetBinContent(i,log_mu)

log_likelihood_plot.SetTitle("Log-Likelihood as a function of #mu")
log_likelihood_plot.GetXaxis().SetTitle("#mu")
log_likelihood_plot.GetYaxis().SetTitle("Log-Likelihood")
log_likelihood_plot.SetStats(0)

canvas.cd()
log_likelihood_plot.Draw("hist")
canvas.Print("../Plots_Notes_HW_100306/Log_likelihood.pdf")
canvas.Clear()
mu_hat = log_likelihood_plot.GetXaxis().GetBinCenter(log_likelihood_plot.GetMaximumBin())
print("\nThe value obtained for mu-hat is {:.2f}.".format(mu_hat))

# Define test-statistics using q0 

q0 = -2*(log_likelihood(0,sighistSEL,bkghistSEL,datahist)-log_likelihood(mu_hat,sighistSEL,bkghistSEL,datahist))

print("\nThe value obtained for q0 is {:.2f}.".format(q0))
print("\nBased on the mu-hat and q0 values, since the mu-hat is > 1 and q0 >> 0, we can argue that the background + signal is the most likely.") 
print("Recall that mu-hat is the Maximum-likelihood estimate for mu and it measures the signal strength. In case it was 0, we had no signal; however, that is not the case (mu-hat is 3.60!).")

MCfile.Close()
datafile.Close()