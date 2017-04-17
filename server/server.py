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

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

@route('/emg-ave', method='POST')
def hert_analyze():
      jsonData = request.json
      print json.dumps(jsonData);
      array = jsonData['emg']
      average = emg.Getave(array)
      body = json.dumps({'average' : average})
      r = HTTPResponse(status=200, body=body)
      r.set_header('Content-Type', 'application/json')
      return r

@route('/heart', method='POST')
def hert_analyze():
     jsonData = request.json
     array = jsonData['array']
     Fxx, Pxx, vlf, lf, hf, isAngry = psdRRi.checkAngry(array)     
     body = json.dumps({'result' : isAngry})
     r = HTTPResponse(status=200, body=body)
     r.set_header('Content-Type', 'application/json')
     return r

@route('/voice', method='POST')
def do_upload():
    # uploadプロパティから音声ファイルを取得
    upload = request.files.get('upload2', '')
    if not upload.filename.lower().endswith(('.wav')):
        return 'File extension not allowed!'
    # tempfileの名前を取得してそこに保存
    tf = tempfile.NamedTemporaryFile()
    upload.save(tf.name, True)
    # Vokaturiをして解析
    result = vokaturi.analyze(tf.name)
    # 解析結果を保存
    body = json.dumps({'result' : result})
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
    emgAve = jsonData['emg-ave']
    emgList = jsonData['emg']
    heartrate = jsonData['heartrate']
    sendTime = jsonData['send-time']
    
    # 結果を入れる辞書型を作成 返す送信時間を入れる
    result = {"send-time" : sendTime}
    
    # 心拍を解析
    result.update({"heartrate" : {"result" : False}})    

    # 筋電を解析
    result.update({"emg" : {"result" : emg.EmgAnarayze(emgList, emgAve)}})
    
    # 音声を解析
    tf = tempfile.NamedTemporaryFile()
    voice.save(tf.name, True)
    result.update({"voice" : {"result" : vokaturi.analyze(tf.name)}})
    
    # 写真を解析
    rf = tempfile.NamedTemporaryFile()
    face.save(rf.name, True)
    result.update({"face" : {"result" : True}})

    # 本質的な怒りを解析
    angryBody = False
    result.update({"angry-body" : angryBody})
    
    # 見た目の怒りを解析
    angryLook = True
    result.update({"angry-look" : angryLook})

    # ギャップを解析
    angryGap = False
    if angryBody != angryLook :
        angryGap = True
    result.update({"angry-gap" : angryGap})
       
    # 解析結果をjsonにしてアップロード 
    body = json.dumps(result)
    r = HTTPResponse(status=200, body=body)
    r.set_header('Content-Type', 'application/json')
    return r


run(host="0.0.0.0", port=8080, debug=True, reloader=True)
