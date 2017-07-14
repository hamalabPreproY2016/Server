# vim:fileencoding=utf-8
from bottle import route, run, template, request, static_file, url, get, post, response, error, abort, redirect, os, HTTPResponse
import sys, codecs
import bottle.ext.sqlalchemy
import sqlalchemy
import sqlalchemy.ext.declarative
import simplejson as json
import tempfile
import analyzer.analyze_angry as analyze_angry
import analyzer.emg as emg
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
PRECISION = 6
@route('/checker', method='GET')
def Checker():
      body = json.dumps({'check' : True})
      r = HTTPResponse(status=200, body=body)
      r.set_header('Content-Type', 'application/json')
      return r


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

    mve = jsonData['emg-mve']
    emg_arr = jsonData['emg']
    heart_arr = jsonData['heartrate']
    sendTime = jsonData['send-time']
    
    temp_voice = tempfile.NamedTemporaryFile()
    voice_path = temp_voice.name
    voice.save(voice_path, True)
    
    temp_face = tempfile.NamedTemporaryFile()
    face_path = temp_face.name
    face.save(face_path, True)
    # face.save("./temp.jpg"True)
    
    # f = open('write.json', 'w')
    # f.write(json.dumps(jsonData))
    # f.close() 
    
    # 結果を入れる辞書型を作成 返す送信時間を入れる
    result = {"send-time" : sendTime}
    
    # 各センサー値を解析
    heart_angry, emg_angry, emg_enabled, voice_angry, voice_enabled, face_angry, face_enabled = analyze_angry.analyzeSensor(heart_arr, emg_arr, voice_path, face_path, mve)

    # 各センサー
    body_angry, look_angry, gap = analyze_angry.analyzeAngry(heart_angry, emg_angry, emg_enabled, voice_angry, voice_enabled, face_angry, face_enabled)

    # 心拍を解析 angryValueを返す
    result.update({"heartrate" : {"angryValue" :  round(heart_angry, PRECISION)}})
    print "analyze-hertrate : angry " + str('%03.3f' % heart_angry)   

    # 筋電を解析 angryValue, isMove
    print "analyze-emg      : angry " + str('%03.3f' % emg_angry) + " isMove  " + str(emg_enabled)
    result.update({"emg" : {"angryValue" : round(emg_angry, PRECISION), "isMove" : emg_enabled}})
    
    # 音声を解析 angryValue, enabled
    print "analyze-voice    : angry " + str('%03.3f' % voice_angry) + " enabled " + str(voice_enabled) 
    result.update({"voice" : {"angryValue" :  round(voice_angry, PRECISION), "enabled" : voice_enabled}})
    
    # 写真を解析 angryValue, isFace
    print "analyze-face     : angry " + str('%03.3f' % face_angry) + " isFace  " + str(face_enabled) 
    result.update({"face" : {"angryValue" : round(face_angry, PRECISION), "isFace" : face_enabled}})
    
    print " "

    # 本質的な怒りを解析
    print "analyze-body     : " + str('%03.3f' % body_angry) 
    result.update({"angry-body" : round(body_angry, PRECISION)})
    
    # 見た目の怒りを解析
    print "analyze-look     : " + str('%03.3f' % look_angry)
    result.update({"angry-look" : round(look_angry, PRECISION)})

    # ギャップを解析
    print "analyze-gap      : " + str(gap) 
    result.update({"angry-gap" : gap})

    temp_voice.close()
    temp_face.close()
    
    # 解析結果をjsonにしてアップロード 
    body = json.dumps(result)
    r = HTTPResponse(status=200, body=body)
    r.set_header('Content-Type', 'application/json')
    return r


run(host="0.0.0.0", port=8080, debug=True, reloader=True)
