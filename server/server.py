# vim:fileencoding=utf-8
from bottle import route, run, template, request, static_file, url, get, post, response, error, abort, redirect, os, HTTPResponse
import sys, codecs
import bottle.ext.sqlalchemy
import sqlalchemy
import sqlalchemy.ext.declarative
import vokaturi
import psdRRi
import simplejson as json
import tempfile
import emg
import subprocess
from discrimination import disc
import angry_predict
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
 
@route('/emg-mve', method='POST')
def EmgMVE():
      jsonData = request.json
      array = jsonData['emg']
      mve = emg.GetMve(array)
      print "mve : " + str(mve)
      body = json.dumps({'mve' : mve})
      r = HTTPResponse(status=200, body=body)
      r.set_header('Content-Type', 'application/json')
      return r

@route('/angry', method='POST')
def do_upload():
    # プロパティからデータを取得
    voice = request.files.get('voice', '')
    if not voice.filename.lower().endswith(('.wav')):
        return 'File extension not allowed!'
    face = request.files.get('face', '')
    if not face.filename.lower().endswith('.jpg'):
        return 'File extension not allowed!!'
    jsonData = json.loads(request.forms.get('json'))
    emgAve = jsonData['emg-mve']
    emgList = jsonData['emg']
    heartrate = jsonData['heartrate']
    sendTime = jsonData['send-time']
    mve = 500 
    f = open('write.json', 'w')
    f.write(json.dumps(jsonData))
    f.close() 
    # 結果を入れる辞書型を作成 返す送信時間を入れる
    result = {"send-time" : sendTime}
    
    # 心拍を解析 angryValueを返す
    Fxx, Pxx, vlf, lf, hf, heartRateAngry = psdRRi.checkAngry(heartrate)
    result.update({"heartrate" : {"angryValue" :  heartRateAngry}})
    print "analyze-hertrate : angry " + str('%03.3f' % heartRateAngry)   

    # 筋電を解析 angryValue, isMove
    isEnabledEmg, emgAngry = emg.EmgAnarayze(emgList, emg)
    print "analyze-emg      : angry " + str(emgAngry) + " isMove " + str(isEnabledEmg)
    result.update({"emg" : {"angryValue" : emgAngry, "isMove" : isEnabledEmg}})
    
    # 音声を解析 angryValue, enabled
    tf = tempfile.NamedTemporaryFile()
    voice.save(tf.name, True)
    subprocess.call( ["sh", "wavConverter.sh", str(tf.name)] )
    isEnabledVoice, voiceAngry = vokaturi.analyze(tf.name)
    print "analyze-voice    : angry " + str('%03.3f' % voiceAngry) + " enabled " + str(isEnabledVoice) 
    result.update({"voice" : {"angryValue" :  voiceAngry, "enabled" : isEnabledVoice}})
    tf.close()
    
    # 写真を解析 angryValue, isFace
    rf = tempfile.NamedTemporaryFile()
    face.save(rf.name, True)
    face.save("./temp.jpg", True)
    isEnabledFace, faceAngry = disc(rf.name)
    print "analyze-face     : angry " + str('%03.3f' % faceAngry) + " isFace " + str(isEnabledFace) 
    result.update({"face" : {"angryValue" : faceAngry, "isFace" : isEnabledFace}})
    rf.close()
    
    print " "


    angryBody, angryLook = angry_predict.angry_predict(heartRateAngry, emgAngry, isEnabledEmg, faceAngry, isEnabledFace, voiceAngry, isEnabledVoice);

    
    # 本質的な怒りを解析
    print "analyze-body     : " + str(angryBody) 
    angryBody = True if angryBody > 0.5 else False
    result.update({"angry-body" : angryBody})
    
    # 見た目の怒りを解析
    print "analyze-look     : " + str(angryLook)
    angryLook = True if angryLook > 0.5 else False
    result.update({"angry-look" : angryLook})

    # ギャップを解析
    angryGap = angryBody != angryLook
    print "analyze-gap      : " + str(angryGap) 
    result.update({"angry-gap" : angryGap})
    # 解析結果をjsonにしてアップロード 
    body = json.dumps(result)
    r = HTTPResponse(status=200, body=body)
    r.set_header('Content-Type', 'application/json')
    return r


run(host="0.0.0.0", port=8080, debug=True, reloader=True)
