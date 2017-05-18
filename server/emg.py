# vim:fileencoding=utf-8

import csv

#累積分布関数を代入する配列
#%MVE0.000〜0.399の範囲の確率を代入
#配列の番号*0.001が%MVEの値
#配列の値が確率
array = []

#累積分布関数の作成
def accumulation() :
    #怒り状態の累積分布関数のデータファイル読み込み
    with open('hogehoge.csv', 'r') as f:
        reader = csv.reader( f )

        # 配列に代入
        for row in reader :
            array.append( float(row[0]) )


# 送られてきた配列のデータでの怒り判別関数
def allAngryjudge( arr, mve ) :

    # 動いているか動いていないかのカウント
    mfe_count = 0 #動いていない
    afe_count = 0 #動いている
    # 結果を加算していく
    sumResult = 0.0
    #動いているかいないかのフラグ
    move_flag = False


    for i in range( len(arr) ) :
        #現在の%MVE
        nowmve = arr[ i ] / mve

        #現在の%MVEが0.4以下の場合　→　動いていないので怒りの判別を行う
        if nowmve < 0.4 :
            sumResult += array[ int(nowmve*100) ]
            print( array[ int(nowmve*100) ] )
            mfe_count += 1

        #現在の%MVEが0.4以上場合　→　動いているので怒りの判別を行わない
        else :
            afe_count += 1

    #結果
    #動いている場合
    if mfe_count < afe_count :
        emgResult = 0
        move_flag = True
    #動いていない場合
    else :
        emgResult = sumResult / mfe_count

    return move_flag, emgResult


if __name__ == '__main__' :
    accumulation()

    testdata = [ 177, 255, 345, 700, 840 ]
    testmve = 890

    print( allAngryjudge( testdata, testmve ) )
