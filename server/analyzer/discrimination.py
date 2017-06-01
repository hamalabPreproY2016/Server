
# python facial_landmarks.py --shape-predictor shape_predictor_68_face_landmarks.dat --image images/example_01.jpg 

# import the necessary packages
from imutils import face_utils
import subprocess
from sklearn.externals import joblib
import numpy as np
import argparse
import imutils
import dlib
import cv2
import sys
import csv
import os
import glob
import math
import re
import pandas as pd
import tempfile
import warnings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings("ignore", message="numpy.dtype size changed")
warnings.filterwarnings("ignore", message="numpy.ufunc size changed")

base = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.normpath(os.path.join(base, "facialfeatures_model20170525.csv"))
dat_path = os.path.normpath(os.path.join(base, "shape_predictor_68_face_landmarks.dat"))
pkl_path = os.path.normpath(os.path.join(base, "preproY2016SVMModel20170525.pkl"))

global model_data
model_data = np.genfromtxt(open(csv_path, "rb"), delimiter=",",usecols=np.arange(0,54672), dtype=float)

def disc(file):
	warnings.filterwarnings("ignore", message="numpy.dtype size changed")
	warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
	detector = dlib.get_frontal_face_detector()
	predictor = dlib.shape_predictor(dat_path)
	arr_cal = []
	arr_label = []
	max = 0
	d = ""
	image = cv2.imread(file)
	image = imutils.resize(image, width=500)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	rects = detector(gray, 1)
        if len(rects) == 0:
                return False, 0 
	for (i, rect) in enumerate(rects):
		shape = predictor(gray, rect)
		shape = face_utils.shape_to_np(shape)
		(x, y, w, h) = face_utils.rect_to_bb(rect)
		cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
		cv2.putText(image, "Face #{}".format(i + 1), (x - 10, y - 10),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
		arr = [[0 for i in range(2)] for j in range(68)]	
		n = 0
		for (x, y) in shape:
			cv2.circle(image, (x, y), 1, (0, 0, 255), -1)
			arr[n][0] = x
			arr[n][1] = y 
			n += 1
		if n < 68:
			return False, 0
		for num1 in range(68):
			for num2 in range(68):
				if num2 > num1:
					for num3 in range(68):
						if num3 > num2:
							tmp = abs((arr[num2][0]-arr[num1][0])*(arr[num3][1]-arr[num1][1]) - (arr[num2][1]-arr[num1][1])*(arr[num3][0]-arr[num1][0]))
							d += str(tmp)
							d += ","
		for num1 in range(68):
			for num2 in range(68):
				if num2 > num1:
					tmp = math.sqrt(pow(arr[num1][0]-arr[num2][0],2)+pow(arr[num1][1]-arr[num2][1],2))
					d += str(tmp)
					d += ","
		max=0
		for num1 in range(68):
			for num2 in range(68):
				if num2 > num1:
					t = math.sqrt(abs(arr[num1][0]-arr[num2][0])*abs(arr[num1][0]-arr[num2][0]) + abs(arr[num1][1]-arr[num2][1])*abs(arr[num1][1]-arr[num2][1]))
					if t != 0:
						tmp = (arr[num1][0]-arr[num2][0])/(math.sqrt(abs(arr[num1][0]-arr[num2][0])*abs(arr[num1][0]-arr[num2][0]) + abs(arr[num1][1]-arr[num2][1])*abs(arr[num1][1]-arr[num2][1])))
						d += str(tmp)
						d += ","
						if tmp > max:
							max = tmp
					else:
						d += str(max)
						d += ","
	tn = tempfile.NamedTemporaryFile()
	fp = open(tn.name,'w')
	# print "Debug(Got file name) :" + fp.name
	fp.write(d)
	fp.close()
	X_t = np.genfromtxt(open(tn.name, "rb"), delimiter=",",usecols=np.arange(0,54672), dtype=float)
	X = X_t.reshape(1,-1)
	sc = StandardScaler()
	#sc.fit(X)
	sc.fit(model_data)
	X_std = sc.transform(X)
	clf = joblib.load(pkl_path)
	r = clf.predict_proba(X_std.reshape(1,-1))
        tn.close()
        return True, r[0][1]

