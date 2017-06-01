# vim:fileencoding=utf-8

# ネットワーク構築
from keras.models import Sequential, model_from_json, load_model
from keras.layers import Dense, Activation

# 学習プロセス
from keras.optimizers import SGD

# コールバック
from keras.callbacks import ModelCheckpoint

import numpy as np
from numpy.random import *

import os
base = os.path.dirname(os.path.abspath(__file__))
MODEL_NAME = os.path.normpath(os.path.join(base, 'angry_look.hdf5'))

# 学習させる関数
def fit(X_train, y_train, model_name = MODEL_NAME):

    # 初期化
    model = Sequential()

    # 層の追加
    model.add(Dense(output_dim=3, input_dim=2))
    model.add(Activation("relu"))
    model.add(Dense(output_dim=2))
    model.add(Activation("softmax"))

    # optimizer = "sgd"でも、簡単に最適化関数の設定ができる
    #(その場合パラメータはデフォルト値)
    model.compile(loss="categorical_crossentropy",
                  optimizer=SGD(lr=0.01, momentum=0.9, nesterov=True),
                  metrics=["accuracy"])

    # コールバックで学習済みモデルの保存
    check = ModelCheckpoint(model_name)

    # 学習開始
    history = model.fit(X_train, y_train, nb_epoch=10,
                        validation_split=0.2, batch_size=32,
                        callbacks=[check])

# ネットワークモデルを評価
def evaluate(X_test, y_test, model_name = MODEL_NAME):
    # モデル評価
    loss_and_metrics = model.evaluate(X_test,y_test,batch_size=32,verbose=0)
    print("\nloss:{} accuracy:{}".format(loss_and_metrics[0],loss_and_metrics[1]))

# 推測
def predict(X_data, model_name = MODEL_NAME):
    # モデル読み込み
    model = load_model(model_name)

    y_result = model.predict(X_data)

    return y_result


if __name__ == '__main__':
    # 動作確認用テスト

    # テストデータ数 x 入力パラメータ数
    # [
    # [表情, 音声],
    # [表情, 音声],
    # [表情, 音声],
    # ...
    # ]
    X_train = rand(10000, 2)

    y_true  = X_train[:, 0] + X_train[:, 1] >= 1.2
    y_false = y_true != True

    # 教師クラスデータ
    # [
    # [真確率, 偽確率],
    # [真確率, 偽確率],
    # [真確率, 偽確率],
    # ...
    # ]
    y_train = np.c_[y_true, y_false]

    # print(y_train)
    #
    # print(X_train.shape)
    # print(y_train.shape)

    fit(X_train, y_train)

    X_test = rand(10, 2)

    y_true  = X_test[:, 0] + X_test[:, 1] >= 1.2
    y_false = y_true != True

    y_test = np.c_[y_true, y_false]

    y_result = predict(X_test)

    print(X_test)

    print(y_test)
    print(y_result)
