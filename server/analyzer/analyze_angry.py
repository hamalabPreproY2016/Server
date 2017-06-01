# vim:fileencoding=utf-8

import psdRRi
import emg
import vokaturi
from discrimination import disc 
import angry_predict
import subprocess
import os

base = os.path.dirname(os.path.abspath(__file__))
converter = os.path.normpath(os.path.join(base, './wavConverter.sh'))

emg.accumulation()

## センサーの値を解析
def analyzeSensor(heart_arr, emg_arr, voice_path, face_path, mve) :
    ## 音声を読み取り可能な形式の変換
    subprocess.call(["sh", converter, str(voice_path)])
    print voice_path 
    ## 心拍を解析
    Fxx, Pxx, vlf, lf, hf, heart_angry = psdRRi.checkAngry(heart_arr)
    ## 筋電を解析
    emg_enabled, emg_angry = emg.allAngryjudge(emg_arr, mve)
    ## 音声を解析
    voice_enabled, voice_angry = vokaturi.analyze(voice_path)
    ## 表情を解析
    face_enabled, face_angry =  disc(face_path)
    return heart_angry, emg_angry, emg_enabled, voice_angry, voice_enabled, face_angry, face_enabled 

## センサーの値から見た目、本質それぞれの怒りの値を取得する
def analyzeAngry(heart_angry, emg_angry, emg_enabled, voice_angry, voice_enabled, face_angry, face_enabled) :
    ## 畳み込みニューラルネットワークで怒りを解析 
    body_angry, look_angry = angry_predict.angry_predict(heart_angry, emg_angry, emg_enabled, face_angry, face_enabled, voice_angry, voice_enabled)
    ## ギャップの有無を求める 
    gap = True if look_angry > 0.5  else False != True if body_angry > 0.5 else False 
    
    return body_angry, look_angry, gap
