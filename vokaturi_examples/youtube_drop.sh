#! /bin/sh

if [ $# -ne 2 ]; then
  echo "指定された引数は$#個です。" 1>&2
  echo "実行するには2個の引数が必要です。" 1>&2
  exit 1
fi
url=$1
title=$2

mkdir `printf $title`

youtube-dl $url -o $title
cd `printf $title`

ffmpeg -i ../`printf $title`.mkv all.wav
rm ../`printf $title`.mkv

ffmpeg -i all.wav -c copy -map 0 -f segment -segment_time 5 %03d.wav


