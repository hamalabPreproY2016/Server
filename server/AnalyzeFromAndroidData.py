# vim:fileencoding=utf-8
import copy
import os
import json
import sys
import subprocess
import csv
import commands
import json
import analyzer.analyze_angry as analyze
import re
from progressbar import ProgressBar
base = os.path.dirname(os.path.abspath(__file__))
expdata = os.path.normpath(os.path.join(base, './expdata'))
FNULL =  open(os.devnull, 'w')
PRECISION = 6

# csvからjsonに変換
def convertDict(inf, typ):
    fi = open(inf, 'rb')
    data = fi.read()
    fi.close()
    fo = open(inf, 'wb')
    fo.write(data.replace('\x00', '') + '\n')
    fo.close()
    print inf
    f = open(inf, 'r')
    reader = csv.reader(f)
    try: 
        headeer = next(reader)
    except StopIteration:
        print "%s は空です" % inf
    count = -1 
    dict_list = []
    num_lines = sum(1 for line in open(inf))
    for row in reader:
        count += 1
        if (len(row) != 2):
            continue
        time = long(0)
        try:
            time = long(row[0])
            value = row[1]
            if (typ is not "string") :
               value = int(row[1])
               if value == 0 and typ == "int" :
                   print value
                   continue
               if (typ is "bool") :
                   value = bool(True if value == 1 else False)
        except ValueError:
            continue
        dict_list.append({"time" : time, "value" : value})
        if (count > num_lines - 3):
            break
    f.close()
    return dict_list

def convertJsonFile(csv_dir, json_dir, name, isNum):    
    url = csv_dir + "/" + name + ".csv"
    dic = convertDict(url, isNum)
    f = open(json_dir + "/" + name + ".json", 'w')
    json.dump(dic, f, indent=4)
    f.close()
    print url

    return dic

def getTeature(dic, begin, time) :
    t_count = 0
    next_begin = len(dic)
    for index in range(begin, len(dic)) :
       if (dic[index]['time'] < time) :
           t_count += 1 if dic[index]['value'] is True else -1
       else:
           next_begin = index
           break
    return False if t_count < 0 else True, next_begin

def HigntAngryFilter(dic):
    tmp_dic = copy.deepcopy(dic) 
    for index in range(len(dic)):
        if (dic[index]['value'] == True) :
            if (index -2 >= 0) :
                tmp_dic[index - 2]['value'] = True
            if (index -1 >= 0) :
                tmp_dic[index - 1]['value'] = True
            if (index + 1 < len(dic)):
                tmp_dic[index + 1]['value'] = True
            if (index + 2 < len(dic)):
                tmp_dic[index + 2]['value'] = True
    return tmp_dic 

def dictToCsv(name, dic):
    temp_l = []
    for index in range(len(dic)) :
        temp_l.append([dic[index]['time'], dic[index]['value']])
    with open(name, 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerows(temp_l)

  
        
# 引数を取得する
argvs = sys.argv
if (len(argvs) < 4):
    print "plese set zippath & lookpath & bodypath"
    exit(0)

zipfile = argvs[1]
lookfile = argvs[2]
bodyfile = argvs[3]

# 展開先ディレクトリを作成
if (os.path.exists(expdata) is not True):
    os.mkdir(expdata)

# zipを展開
cmd = "unzip %s -d %s" % (zipfile, expdata)
subprocess.check_call(cmd.split(" "), stdout=FNULL, stderr=subprocess.STDOUT)
cmd = "ls %s -F -c | grep / | sed -n 1P" % expdata
target_dir = commands.getoutput(cmd)
target_dir = expdata + "/" + target_dir
print "展開ディレクトリ : " + target_dir

# jsonファイルを作成
json_dir = target_dir + "json"
os.mkdir(json_dir)
csv_dir = target_dir + "csv"

# 筋電をjsonへ
emg_dict = convertJsonFile(csv_dir, json_dir, "emg", "int")

# 心拍をjsonへ
hr_dict = convertJsonFile(csv_dir, json_dir, "heartrate", "int")

# 表情をjsonへ
face_dict = convertJsonFile(csv_dir, json_dir, "face", "string")
r = re.compile("(?!.*/).")

for element in face_dict :
    m = r.findall(element['value'])
    element['value'] = target_dir + "image/" + "".join(m)

# 音声をjsonへ
voice_dict = convertJsonFile(csv_dir, json_dir, "voice", "string")
for element in voice_dict :
    m = r.findall(element['value'])
    element['value'] = target_dir + "voice/" + "".join(m)

# MVEをjsonへ
f = open(csv_dir + "/mve.csv", 'r')
mve_str = f.read()
r = re.compile('\"0\",\"([0-9]*)\"')
mve =  int(r.search(mve_str).group(1))
f.close()
url = json_dir + "/mve.json"
f = open(url, 'w')
json.dump({"value" : mve}, f, indent=4)
f.close()

# セッションをjsonへ
session_dict = convertJsonFile(csv_dir, json_dir, "session", "string")

# lookとbody
url = json_dir + "/look.json"
look_dict = convertDict(lookfile, "bool")
f = open(url, 'w')
json.dump(look_dict,f, indent=4)
f.close()
url = json_dir + "/body.json"
body_dict = convertDict(bodyfile, "bool")
f = open(url, 'w')
json.dump(body_dict, f, indent=4)
f.close()

# 怒りを強調させるフィルターをかける
look_dict = HigntAngryFilter(look_dict)
body_dict = HigntAngryFilter(body_dict)
# CSVとして出力
dictToCsv(csv_dir + "/look_F.csv", look_dict)
dictToCsv(csv_dir + "/body_F.csv", body_dict)
exit(0)
end_flg = True 
send_list = []

# 送信データを作成
emg_bn = -1
face_bn = -1
voice_bn = -1
look_bn = 0
body_bn = 0

# 心拍はtimeが0以上のときが基準
for index in range(len(hr_dict)):
    if (hr_dict[index]['time'] >= 0):
        hr_bn = index -1
        break

while end_flg:
    # まず1行読み込む
    emg_bn += 1
    hr_bn += 1
    face_bn += 1
    voice_bn += 1
    emg_stk = []
    hr_stk = []
    face_stk = []
    voice_stk = [] 

    emg_e = emg_dict[emg_bn]
    hr_e = hr_dict[hr_bn]
    face_e = face_dict[face_bn]
    voice_e = voice_dict[voice_bn]

    emg_stk.append(emg_e)
    hr_stk.append(hr_e)
    face_stk.append(face_e)
    voice_stk.append(voice_e)
    
    # 最大取得時間を求め、送信時間とする
    send_time = max(emg_e['time'], hr_e['time'], face_e['time'], voice_e['time'])

    emg_bn += 1
    hr_bn += 1
    face_bn += 1
    voice_bn += 1

    # 各デバイスの配列を探索し、最大取得時間以下のデータをストックしていく
    # 筋電
    for index in range(emg_bn, len(emg_dict)):
        if (send_time < emg_dict[index]['time']):
           break
        emg_stk.append(emg_dict[index])
        emg_bn = index
    # 心拍 最大取得時間までの256個が必要
    for index in range(hr_bn, len(hr_dict)):
        if (send_time < hr_dict[index]['time'] or index + 1 == len(hr_dict)):
            end = index
            if (index + 1 == len(hr_dict)):
                end = len(hr_dict)
            begin = end - 256
            hr_stk = hr_dict[begin:end]
            hr_bn = index - 1
            break
    # 表情 最大取得時間以下でもっとも遅いデータ１つ
    for index in range(face_bn, len(face_dict)):
        if (send_time < face_dict[index]['time']):
            if (face_bn is not index):
                face_stk = []
                face_stk.append(face_dict[index - 1])
                face_bn = index - 1
            break

    # 音声 表情と同じく
    for index in range(voice_bn, len(voice_dict)):
        if (send_time < voice_dict[index]['time']):
            if (voice_bn is not index):
                voice_stk = []
                voice_stk.append(voice_dict[index -1])
                voice_bn = index - 1
            break
    # 見た目をもとめる
    look, look_bn = getTeature(look_dict, look_bn, send_time)

    # 本質をもとめる
    body, body_bn = getTeature(body_dict, body_bn, send_time)

    # 一つでも空だった場合は終了
    if (len(emg_stk) == 0 or len(emg_dict) <= emg_bn + 2 
       or len(hr_stk) == 0 or len(hr_dict) <= hr_bn + 2
       or len(face_stk) == 0 or len(face_dict) <= face_bn + 2
       or len(voice_stk) == 0 or len(voice_dict) <= voice_bn +2
       or len(body_dict) <= body_bn or len(look_dict) <= look_bn):
        break

    # 各解析ストックデータをまとめる
    send_list.append({"emg" : emg_stk, "heartrate" : hr_stk, "face" : face_stk, "voice" : voice_stk, "send_time" : send_time, "mve" : mve, "look" : look, "body" : body})
url = json_dir + "/sendData.json"

f = open(url, 'w')
json.dump(send_list, f, indent=4)
f.close()
result = []
p = ProgressBar(max_value=len(send_list))
count = 0
csv_list = []
# 送信データを元に怒り判定の解析関数に渡す
for element in send_list :
    heart_arr = element['heartrate']
    emg_arr = element['emg']
    voice_path = element['voice'][0]['value']
    face_path = element['face'][0]['value']
    mve = element['mve']
    look_teach = element['look']
    body_teach = element['body']
    send_time = element['send_time']
    heart_angry, emg_angry, emg_enabled, voice_angry, voice_enabled, face_angry, face_enabled = analyze.analyzeSensor(heart_arr, emg_arr, voice_path, face_path, mve)
    heart_angry = round(heart_angry, PRECISION)
    emg_angry = round(emg_angry, PRECISION)
    voice_angry = round(voice_angry, PRECISION)
    face_angry = round(face_angry, PRECISION)
    body_angry, look_angry, gap = analyze.analyzeAngry(heart_angry, emg_angry, emg_enabled, voice_angry, voice_enabled, face_angry, face_enabled)
    body_angry = round(body_angry, PRECISION)
    look_angry = round(look_angry, PRECISION)
    result.append({"heart" : {"value" : heart_angry}, 
                   "emg" : {"value" : emg_angry, "enabled" : emg_enabled},
                   "voice" : {"value" : voice_angry, "enabled" : voice_enabled},
                   "face" : {"value" : face_angry, "enabled" : face_enabled},
                   "body" : body_angry,
                   "look" : look_angry,
                   "look_teach" : look_teach,
                   "body_teach" : body_teach,
                   "gap" : gap,
                   "send_time" : send_time
                  })
    csv_list.append([send_time, heart_angry, emg_angry, emg_enabled, voice_angry, voice_enabled, face_angry, face_enabled, body_angry, look_angry, gap, body_teach, look_teach])
    p.update(count)
    count += 1
url = json_dir + "/angry.json"
f = open(url, 'w')
json.dump(result, f, indent=4)
f.close()
url = csv_dir + "/responseAngryServer.csv"
with open(url, 'w') as f:
    writer = csv.writer(f, lineterminator='\n')
    writer.writerows(csv_list)

exit(0)
#  結果を出して終了
