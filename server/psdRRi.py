#-------------------------------
# Name:        psdRRi
# Purpose:     Estimates the  PSD of given RRi serie and its AUC.
# Author:      Rhenan Bartels Ferreira
# Created:     06/03/2014
# Copyright:   (c) Rhenan 2013
# Licence:     <your licence>
#-------------------------------

import matplotlib.pyplot as plt

from numpy import arange, cumsum, logical_and, clip
from scipy.signal import welch
from scipy.interpolate import splrep, splev

import json

#Calculates the AUC of the PSD
def psdauc(Fxx, Pxx, vlf=0.04, lf=0.15, hf=0.4):
    df = Fxx[1] - Fxx[0]
    rvlf = sum(Pxx[(Fxx <= vlf)]) * df
    rlf = sum(Pxx[logical_and(Fxx >= vlf, Fxx < lf)]) * df
    rhf = sum(Pxx[logical_and(Fxx >= lf, Fxx < hf)]) * df
    return rvlf, rlf, rhf


def psd(rri):
    #Create time array
    t = cumsum(rri) / 1000.0
    t -= t[0]

    #Evenly spaced time array (4Hz)
    tx = arange(t[0], t[-1], 1.0 / 4.0)

    #Interpolate RRi serie
    tck = splrep(t, rri, s=0)
    rrix = splev(tx, tck, der=0)

    #Number os estimations
    P = int((len(tx) - 256 / 128)) + 1

    #PSD with Welch's Method
    Fxx, Pxx = welch(rrix, fs=4.0, window="hanning", nperseg=256, noverlap=128,
                     detrend="linear")

    # print(Fxx)
    # print(Pxx)

    #Plot the PSD
    # plt.plot(Fxx, Pxx)
    # plt.xlabel("Frequency (Hz)")
    # plt.ylabel(r"PSD $(ms^ 2$/Hz)")
    # plt.title("PSD")

    #Calculates the Confidence interval

    from scipy.stats import chi2

    #95% probability
    probability = 0.95

    alfa = 1 - probability
    v = 2 * P
    c = chi2.ppf([1 - alfa / 2, alfa / 2], v)
    c = v / c

    Pxx_lower = Pxx * c[0]
    Pxx_upper = Pxx * c[1]

    # plt.plot(Fxx, Pxx_lower, 'k--')
    # plt.plot(Fxx, Pxx_upper, 'k--')

    # plt.show()

    vlf, lf, hf = psdauc(Fxx, Pxx)

    return Fxx, Pxx, vlf, lf, hf

    # print("vlf:" + vlf + ",lf:" + lf + ",hf:" + hf)
    # print(vlf)
    # print(lf)
    # print(hf)

border = 2.0

LFHF_MAX = 3.0
LFHF_MIN = 1.0

LFHF_RANGE = LFHF_MAX - LFHF_MIN

def checkAngry(array):

    rri = [x["value"] for x in array]

    Fxx, Pxx, vlf, lf, hf = psd(rri);

    angryRate = clip(((lf / hf) - LFHF_MIN) / LFHF_RANGE, 0.0, 1.0)

    # if lf / hf < border:
    #     isAngry = False
    # else:
    #     isAngry = True

    return Fxx, Pxx, vlf, lf, hf, angryRate

if __name__ == '__main__':
    jsonfile = open('angry_request.json', 'r')
    dic = json.load(jsonfile)

    Fxx, Pxx, vlf, lf, hf, angryRate = checkAngry(dic["heartrate"])

    print("angryRate : " + str(angryRate))
