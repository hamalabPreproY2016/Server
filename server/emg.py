# vim:fileencoding=utf-8
# 平常値を取得するための関数 
import math  

# 動いた時の割合
MOVE_RATE = 0.4 
# 怒った時の割合
ANGRY_RATE = 0.002 

# 平均を求める関数
def Getave( c ) :
      sum=0
      for i in range(len(c)):
              sum = sum + c[i]["value"]
      ave = sum/len(c)
      return ave

# MVEを求める関数
# 配列から2要素間隔で平均値を出し、その最大値をMVEとする 
def GetMve( c ) :
    ave_list = []
    for i in range(len(c) / 2):
        begin = i * 2
        f = c[begin]["value"]
        s = c[begin + 1]["value"]
        ave_list.append((int)((f + s) / 2))
    return max(ave_list)

# 送られてきた筋電の配列を解析
def EmgAnarayze(arr, mve) :
    mfe_count = 0
    afe_count = 0
    l = len(arr)
    # 配列の各要素から動いているとき、怒りの時を取得してカウントする
    for i in range(l):
        emg = arr[i]["value"]
        mfe, afe = GetElementAngry(emg, mve)
        mfe_count += 0 if mfe == 0 else 1
        afe_count += 0 if afe == 0 else 1
    mf = False
    af = False
    # 動いている時が多かった場合、怒っていないとする 
    if mfe_count > l / 2 :
        mf = True
        af = False
    if afe_count > l / 2 :
        af = True
    return mf, af

# 筋電とMVEから怒りの判定
def GetElementAngry( emg, mve ) :
    move_flag = False
    angry_flag = False
    # 動いているかどうか
    if emg > MOVE_RATE :
        move_flag = True
    else:
        # 怒りの割合より高いかどうか
        if emg > ANGRY_RATE :
            angry_flag = True
    return move_flag, angry_flag
