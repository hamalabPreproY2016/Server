from bottle import route, run, template, request, static_file, url, get, post, response, error, abort, redirect, os, HTTPResponse
import sys, codecs
import bottle.ext.sqlalchemy
import sqlalchemy
import sqlalchemy.ext.declarative
import vokaturi
import psdRRi
import simplejson as json

sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

#@route("/")
#def html_index():
#    return template("index", url=url)

#@route("/static/<filepath:path>", name="static_file")
#def static(filepath):
#    return static_file(filepath, root="./static")

#@route("/static/img/<img_filepath:path>", name="static_img")
#def static_img(img_filepath):
#    return static_img(img_filepath, root="./static/img/")

#File Upload
#@get('/upload')
#def upload():
#    return '''
#        <form action="/upload" method="post" enctype="multipart/form-data">
#            <input type="submit" value="Upload"></br>
#            <input type="file" name="upload"></br>
#        </form>
#    '''
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
    upload = request.files.get('upload', '')
    if not upload.filename.lower().endswith(('.wav')):
        return 'File extension not allowed!'
    save_path = get_save_path()
    upload.save(save_path, True)
    result = vokaturi.analyze(save_path)
    body = json.dumps({'message' : result})
    r = HTTPResponse(status=200, body=body)
    r.set_header('Content-Type', 'application/json')
    return r

def get_save_path():
    path_dir = "./static/img/000.wav"
    return path_dir
run(host="0.0.0.0", port=8080, debug=True, reloader=True)
