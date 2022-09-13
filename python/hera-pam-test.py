#! /usr/bin/env python

###
# Test HERA PAMS using nanovna
# Configuration 
# NANO VNA port 1 -> 10dB att -> RFOptic Transmitter (port: RF IN) -> Short Fiber -> 
#       PAM under test->10dB att-> Nano VNA port 2
#
# Power PAM with 9V power supply via "rack emulator" board
# Power RFOptic with 5V power supplly
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR
import matplotlib.pyplot as plt
import numpy as np
import datetime
from nanovna import NanoVNA

in_band_gain_good_threshold = 15 
oob_gain_ceiling = 15  #PAM026 at ASU passes this test, but I am suspicious of the nanoVNA in this range
gainoffset = 46

logfile = 'pamtestlog.txt'
print("logging test results to: ", logfile)
PAM = input("Enter PAM Serial Number: ")
POL = input("Enter Polarization E/N: ")

def dBP(x):
 return 20*np.log10(x)
# create instance and connect to the device
nv = NanoVNA()

#set frequency range
# nominal PAM passpand is 50 to 250MHz, but it has gain out to 600MHz
# we will check 1) that the gain is high enough in the passband, and low enough in the reject band
nv.set_sweep(1e6, 600e6)
nv.fetch_frequencies()


#log the data and the current time it was taken
now = datetime.datetime.now().strftime('%Y-%m-%d-%H%M')
s12 = nv.data(1)

fig,axs = plt.subplots(2,1,sharex=True)
axs[0].plot(nv.frequencies/1e6,dBP(np.abs(s12))+gainoffset)
axs[1].plot(nv.frequencies/1e6,np.angle(s12))
axs[0].set_xlabel('MHz')
axs[0].set_ylabel('dB')
axs[1].set_xlabel('MHz')
axs[1].set_ylabel('rad')


titletext = "PAM: "+PAM + POL

median_gain = np.median(dBP(np.abs(s12[nv.frequencies<250e6]))+gainoffset)
in_band_gain_good = median_gain>in_band_gain_good_threshold
print("       median gain [ 60 to 250MHz]:",median_gain,end='\r')
if in_band_gain_good: 
    print(bcolors.OK+"[OK]"+bcolors.RESET)
    titletext += " GAIN [OK]"
    gaintxt = 'OK'
else: 
    print(bcolors.FAIL+"[LOW]"+bcolors.RESET)
    titletext += " GAIN [LOW]"
    gaintxt = 'LOW'


max_gain_oob = np.max(dBP(np.abs(s12[nv.frequencies>250e6]))+gainoffset)
print("         max gain [250 to 600MHz]:",max_gain_oob,end='\r')
if max_gain_oob <oob_gain_ceiling:  
    print(bcolors.OK + "[OK]" +  bcolors.RESET)
    titletext += " OOB GAIN [OK]"
    OOBtxt = 'OK'
else: 
    print(bcolors.FAIL + "[HIGH]" + bcolors.RESET)
    titletext += " OOB GAIN [TOO HIGH!]"
    OOBtxt = 'HIGH'

fig.suptitle(titletext)

#log this result to the running log
F = open(logfile,'a')
F.write(now+','+PAM+','+ str(median_gain)+','+ gaintxt \
     +','+str(max_gain_oob)+','+OOBtxt+"\n")
F.close()


filename = 'nanovna.pam.'+PAM+POL+"."+now
print('saving data and plot to:')
print("    "+filename+'.npz')
print("    "+filename+'.png')
np.savez(filename+'.npz',freqs=nv.frequencies,s12=s12)

plt.savefig(filename+'.jpg')
plt.show()

