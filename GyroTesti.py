import time
import statistics
import numpy as np
import general_functions as fnc

def check_calibration_test(sensor_data, max_gyro_value, min_gyro_value, min_gyro_X_value, max_gyro_X_value, min_gyro_Y_value, max_gyro_Y_value, min_gyro_Z_value, max_gyro_Z_value, var_gyro_value):

    result = {
                "GyroNormValue": False,
                "GyroXValue": False,
                "GyroYValue": False,
                "GyroZValue": False,
                "GyroValue": False,
                "GyroXVar": False,
                "GyroYVar": False,
                "GyroZVar": False,
                "GyroVar": False,
                "GyroResult": False,
<<<<<<< HEAD
                "MinGyroX": 0.0,
                "MaxGyroX": 0.0,
                "MinGyroY": 0.0,
                "MaxGyroY": 0.0,
                "MinGyroZ": 0.0,
                "MaxGyroZ": 0.0,
=======
>>>>>>> 61722c604d416dc33fed4d5583b26a493a8f5371
    }

    mean_gyro_X = np.mean(sensor_data.gyroX)
    mean_gyro_Y = np.mean(sensor_data.gyroY)
    mean_gyro_Z = np.mean(sensor_data.gyroZ)

<<<<<<< HEAD
    result["MinGyroX"] = np.min(sensor_data.gyroX)
    result["MaxGyroX"] = np.max(sensor_data.gyroX)
    
    result["MinGyroY"] = np.min(sensor_data.gyroY)
    result["MaxGyroY"] = np.max(sensor_data.gyroY)
    
    result["MinGyroZ"] = np.min(sensor_data.gyroZ)
    result["MaxGyroZ"] = np.max(sensor_data.gyroZ)

=======
>>>>>>> 61722c604d416dc33fed4d5583b26a493a8f5371
    gyro_Norm = np.sqrt(
            mean_gyro_X ** 2 + 
            mean_gyro_Y ** 2 + 
            mean_gyro_Z ** 2
            )

    if min_gyro_value <= gyro_Norm <= max_gyro_value:
        result["GyroNormValue"] = True
    else:
        result["GyroNormValue"] = False

    if ((sensor_data.gyroX >= min_gyro_X_value) & (sensor_data.gyroX <= max_gyro_X_value)).all():
        result["GyroXValue"] = True
    else:
        result["GyroXValue"] = False

    if ((sensor_data.gyroY >= min_gyro_Y_value) & (sensor_data.gyroY <= max_gyro_Y_value)).all():
        result["GyroYValue"] = True
    else:
        result["GyroYValue"] = False

    if ((sensor_data.gyroZ >= min_gyro_Z_value) & (sensor_data.gyroZ <= max_gyro_Z_value)).all():
        result["GyroZValue"] = True
    else:
        result["GyroZValue"] = False

    result["GyroValue"] = result["GyroXValue"] and result["GyroYValue"] and result["GyroZValue"]

    gyro_X_20_sample = sensor_data.gyroX[:20]
    gyro_Y_20_sample = sensor_data.gyroY[:20]
    gyro_Z_20_sample = sensor_data.gyroZ[:20]
    
    Var_Gyro_X = statistics.variance(gyro_X_20_sample)
    Var_Gyro_Y = statistics.variance(gyro_Y_20_sample)
    Var_Gyro_Z = statistics.variance(gyro_Z_20_sample)

    if Var_Gyro_X != 0 and 0 <= Var_Gyro_X <= var_gyro_value:
        result["GyroXVar"] = True
    else:
        result["GyroXVar"] = False

    if Var_Gyro_Y != 0 and 0 <= Var_Gyro_Y <= var_gyro_value:
        result["GyroYVar"] = True
    else:
        result["GyroYVar"] = False

    if Var_Gyro_Z != 0 and 0 <= Var_Gyro_Z <= var_gyro_value:
        result["GyroZVar"] = True
    else:
        result["GyroZVar"] = False

    result["GyroVar"] = result["GyroXVar"] and result["GyroYVar"] and result["GyroZVar"]

    result["GyroResult"] = result["GyroNormValue"] and result["GyroValue"] and result["GyroVar"]
    
    return result

def test_gyro(dlg, base_path, gyro_folder,  max_gyro_value, min_gyro_value, min_gyro_X_value, max_gyro_X_value, min_gyro_Y_value, max_gyro_Y_value, min_gyro_Z_value, max_gyro_Z_value, var_gyro_value, sleep_time):

    #print("Hard reset")

    time.sleep(2)

    log_gyro_acilis = fnc.auto_start(dlg, base_path, gyro_folder, sleep_time)

    try:
        sensor_data_gyro_acilis = fnc.parse_log(log_gyro_acilis)
    except (FileNotFoundError, ValueError) as e:
        return None
     
            
    results_calib_test = check_calibration_test(sensor_data_gyro_acilis,  max_gyro_value, min_gyro_value, min_gyro_X_value, max_gyro_X_value, min_gyro_Y_value, max_gyro_Y_value, min_gyro_Z_value, max_gyro_Z_value, var_gyro_value)

<<<<<<< HEAD
    if results_calib_test["GyroResult"] == True:
        print("Test 4: BAŞARILI")
    elif results_calib_test["GyroResult"] == False:
        print("Test 4: BAŞARISIZ")
        if results_calib_test["GyroNormValue"] == False:
            print("Gyro Norm Hatalı")
        if results_calib_test["GyroXValue"] == False:
            print("Gyro X Değer Aralığı Yanlış")
        if results_calib_test["GyroYValue"] == False:
            print("Gyro Y Değer Aralığı Yanlış")
        if results_calib_test["GyroZValue"] == False:
            print("Gyro Z Değer Aralığı Yanlış")
        if results_calib_test["GyroXVar"] == False:
            print("Gyro Var X Değer Aralığı Yanlış")
        if results_calib_test["GyroYVar"] == False:
            print("Gyro Var Y Değer Aralığı Yanlış")
        if results_calib_test["GyroZVar"] == False:
            print("Gyro Var Z Değer Aralığı Yanlış")
        if results_calib_test["GyroNormValue"] or results_calib_test["GyroValue"] or results_calib_test["GyroVar"]:
            print("BAŞARISIZ")

=======
>>>>>>> 61722c604d416dc33fed4d5583b26a493a8f5371
    return results_calib_test