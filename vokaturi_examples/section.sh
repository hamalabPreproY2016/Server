#! /bin/sh

if [ $# -ne 1 ]; then
  echo "指定された引数は$#個です。" 1>&2
  echo "実行するには1個の引数が必要です。" 1>&2
  exit 1
fi

all=`ls -F $1| grep -v / | wc -l`
echo "ファイル総数" $all
count=`expr $all - 2`
echo "wav-last-number" $count

: > `printf $1`.csv
echo ",Neutral,Happy,Sad,Angry,Fear" >> `printf $1`.csv 
for i in `seq -f %03g 0 $count`
do
printf `expr $i \* 5` >> `printf $1`.csv
printf ',' >> `printf $1`.csv
python2 vokaturi.py `printf $1`/`printf $i`.wav |sed -r -e '1,10d; s/((Neutral)|(Happy)|(Sad)|(Angry)|(Fear)): (.+)/\7,/;' | tr -d '\n' >> `printf $1`.csv
echo -n "\n" >> `printf $1`.csv
echo ${i}
done

echo "終わり"


