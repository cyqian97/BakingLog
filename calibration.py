from ThermocoupleFit import k_type_fit_inverse
import numpy as np

def calibrate(multimeterRead, arduinoRead):
    f = k_type_fit_inverse()
    tcOutput = f(multimeterRead)
    arduinoInput = np.array(arduinoRead) / 4096 * 3.3
    coef = np.polyfit(tcOutput, arduinoInput, 1)
    return coef

multimeterRead = [45, 127.6, 133.4, 139.2, 161.3, 167.6]
arduinoRead = [66.6,343.5,361.53,375.6,450.4,469.68]
print(calibrate(multimeterRead, arduinoRead))

multimeterRead = [39.2, 126.0, 139.1, 141.2, 159.5, 165.8]
arduinoRead = [41.4, 325.8, 371.21, 377.98, 440.0, 459.74]
print(calibrate(multimeterRead, arduinoRead))




# multimeterRead = [45, 127.6, 133.4, 139.2, 161.3, 167.6]
# arduinoRead = [66.6,343.5,361.53,375.6,450.4,469.68]
# f = k_type_fit_inverse()
# tcOutput = f(multimeterRead)
# arduinoInput = np.array(arduinoRead)/4096*3.3
# coef = np.polyfit(tcOutput,arduinoInput,1)
# print(coef)
#
# multimeterRead = [45, 127.6, 133.4, 139.2, 161.3, 167.6]
# arduinoRead = [66.6,343.5,361.53,375.6,450.4,469.68]
# f = k_type_fit_inverse()
# tcOutput = f(multimeterRead)
# arduinoInput = np.array(arduinoRead)/4096*3.3
# coef = np.polyfit(tcOutput,arduinoInput,1)
# print(coef)
