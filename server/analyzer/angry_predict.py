# vim:fileencoding=utf-8

import angry_look_predict as look
import angry_body_predict as body

import numpy as np
from numpy.random import *

# 怒りを判定
def angry_predict(heartrate, myo, myoEnable, face, faceEnable, voice, voiceEnable):
    # bodyInput = np.array([[heartrate, myo, myoEnable]])
    # lookInput = np.array([[face, voice]])
    #
    # bodyResult = body.predict(bodyInput)
    # lookResult = look.predict(lookInput)

    # return bodyResult[0][0], lookResult[0][0]

    bodyResult = heartrate * 0.5 + myo * 0.5 * myoEnable
    lookResult = face * 0.7 * faceEnable + voice * 0.3 * voiceEnable

    return bodyResult, lookResult

if __name__ == '__main__':
    bodyResult, lookResult = angry_predict(0.2, 0.3, True, 0.7, True, 0.8, True)

    print(bodyResult)
    print(lookResult)
