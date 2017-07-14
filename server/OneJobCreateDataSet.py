# vim:fileencoding=utf-8
import copy
import os
import json
import sys
import subprocess
import csv
import commands
import json
import createDataSet

import re

class Type :
    LOOK = 0
    BODY = 1
    ZIP = 2
    FAILE = 3
    message = ["could not found look",
            "could not found body",
            "could not found zip",
            "this data is failed-Data, skip now"]

# ファイル検索用の正規表現をコンパイル

re_list = [None] * 4
re_list[Type.LOOK] = re.compile(".+look.+\.csv") 
re_list[Type.BODY] = re.compile(".+body.+\.csv") 
re_list[Type.ZIP] = re.compile(".+\.zip")
re_list[Type.FAILE] = re.compile(".+failed-data\.txt")


# 引数から変換前のデータが入っているディレクトリを取得する
argvs = sys.argv
if (len(argvs) < 2):
    print "plese set DataSetPath"
    exit(0)

list_dir = argvs[1]

# 各実験ディレクトリリストを取得する
files = os.listdir(list_dir)
files_dir = [os.path.join(list_dir, f) for f in files if os.path.isdir(os.path.join(list_dir, f))]
# 一つずつ実行していく
for target_dir in files_dir :
   print '-----------------------------------------------------'
   print target_dir
   # 各実験ディレクトリ内のファイルリストを取得する
   files = os.listdir(target_dir)
   files_file = [os.path.join(target_dir, f) for f in files if os.path.isfile(os.path.join(target_dir, f))]
   target_file = [""] * 4
   # ディレクトリにlookとbodyとzipが存在するか確認する
   # 存在しないファイルがあるならばスキップする
   for fi  in files_file :
       dog = 0
       for index in range(len(re_list)) :
           if re_list[index].match(fi) :
              target_file[index] = fi
              break 
           dog += 1
       if dog < 4:
           target_file[dog] = fi
   if target_file[3] is not "":
       print Type.message[3]
       continue
   for index in range(3) :
        if target_file[index] is "" :
            print Type.message[index]
            continue
   print target_file[Type.ZIP]
   print target_file[Type.LOOK]
   print target_file[Type.BODY]
   createDataSet.createDataSet(target_file[Type.ZIP], target_file[Type.LOOK], target_file[Type.BODY])
