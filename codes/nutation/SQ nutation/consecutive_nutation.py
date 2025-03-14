import fileinput
import sys
import os
import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
from pyfonts import load_font
font = load_font(
   font_url="https://github.com/jondot/dotfiles2/blob/master/.fonts/cambria.ttf?raw=true"
)
left = 0
right = 0
step = 0
CQ = np.array([10000, 50000])
CQ_labels_khz = np.divide(CQ, 1000)
large_cq = np.array([])
idx=0
for cq in CQ_labels_khz:
  if cq>=1000:
    large_cq = np.insert(large_cq, idx, cq)
    idx+=1
CQ_labels_mhz = np.divide(large_cq, 1000)
  
def generateParams():
  global left
  global right
  global step
  left = float(input("Enter minimal value for your parameter"))
  right = float(input("Enter maximal value for your parameter"))
  step = float(input("Enter step size for your parameter"))
  return np.arange(left, right+step, step).tolist()

file = "nutation.in"
T1params_to_change = generateParams()
prevT1 = T1params_to_change[0]
nextT1 = T1params_to_change[0]
prevCQ = CQ[0]
nextCQ = CQ[0]
T1line = 18
CQline = 4
index = 0
CQ_index = 0
T1_baseline = "variable T1 "
CQ_baseline = "quadrupole 1 1 "
CQ_baseline2 = " 0.6 0 0 0"
norm = 8

def replacement(lineNum, content):
  data = open('nutation.in', 'r').readlines()
  data[lineNum-1] = '{}\n'.format(content)
  fileq =  open('nutation.in', 'w')
  fileq.writelines(data)
 
def runSimulations(index, prevT1):     
  while (index < len(T1params_to_change)):
    os.system("simpson nutation.in")
    index = index+1
    nextT1 = T1params_to_change[index if index < len(T1params_to_change) else 0]
    print("prev T1=", prevT1, "next T1=", nextT1) 
    replacement(T1line, T1_baseline + str(prevT1))
    prevT1 = nextT1
  print("simulations done!")

replacement(CQline, CQ_baseline + str(CQ[0]) + CQ_baseline2) 
while (CQ_index < len(CQ)):
  os.system("rm *.fid")      
  replacement(T1line, T1_baseline + str(prevT1))
  print("CQ={}".format(CQ[CQ_index]))
  print("CQ INDEX =   ", CQ_index)
  runSimulations(index, prevT1)
  
  filenames = [f for f in os.listdir("./") if f.endswith('.fid')]
  filenames = sorted(filenames, key=os.path.getmtime)
  first_points = [(np.loadtxt(filename,usecols=(1))) for filename in filenames]
  first_points_arr = np.array(first_points)/norm
  if CQ[CQ_index] >= 1e6:
    plt.plot(T1params_to_change[:-1], first_points_arr, label="Cq={}MHz".format(int(CQ_labels_mhz[CQ_index-len(CQ_labels_khz)])))
  else:
    plt.plot(T1params_to_change[:-1], first_points_arr, label="Cq={}kHz".format(int(CQ_labels_khz[CQ_index])))
  
  CQ_index = CQ_index+1
  replacement(CQline, CQ_baseline + str(CQ[CQ_index if CQ_index < len(CQ) else 0]) + CQ_baseline2)


plt.legend(loc="lower left")
plt.annotate('(a)', xy=(0.02, 0.92), xycoords="axes fraction", font=font, fontsize=14)
#plt.title("intensity of signal VS Pulse duration")
plt.xlabel("Irradiation duration [\u03BCs]")
#locs, labels = plt.yticks()
#labels = np.linspace(-1.2, 1.2, len(locs))
#labels_list = ['%.1f' % a for a in labels]
#plt.yticks(locs, labels_list)
#plt.gca().yaxis.set_major_formatter(FormatStrFormatter('%1.1f'))
plt.savefig("nutation-Cs-SQ-test.png", dpi=300)
plt.show()