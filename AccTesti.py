import time
import statistics
import numpy as np
import general_functions as fnc

def check_calibration_test(sensor_data, max_norm_value, min_norm_value, min_acc_X_value, max_acc_X_value, min_acc_Y_value, max_acc_Y_value, min_acc_Z_value, max_acc_Z_value, var_acc_value):

    result = {
                "AccNormValue": False,
                "AccXValue": False,
                "AccYValue": False,
                "AccZValue": False,
                "AccValue": False,
                "AccXVar": False,
                "AccYVar": False,
                "AccZVar": False,
                "AccVar": False,
                "AccResult": False,
<<<<<<< HEAD
                "MinAccX": 0.0,
                "MaxAccX": 0.0,
                "MinAccY": 0.0,
                "MaxAccY": 0.0,
                "MinAccZ": 0.0,
                "MaxAccZ": 0.0,
=======
>>>>>>> 61722c604d416dc33fed4d5583b26a493a8f5371
    }

    mean_acc_X = np.mean(sensor_data.accX)
    mean_acc_Y = np.mean(sensor_data.accY)
    mean_acc_Z = np.mean(sensor_data.accZ)

<<<<<<< HEAD
    result["MinAccX"] = np.min(sensor_data.accX)
    result["MaxAccX"] = np.max(sensor_data.accX)

    result["MinAccY"] = np.min(sensor_data.accY)
    result["MaxAccY"] = np.max(sensor_data.accY)

    result["MinAccZ"] = np.min(sensor_data.accZ)
    result["MaxAccZ"] = np.max(sensor_data.accZ)

=======
>>>>>>> 61722c604d416dc33fed4d5583b26a493a8f5371

    acc_Norm = np.sqrt(
            mean_acc_X ** 2 + 
            mean_acc_Y ** 2 + 
            mean_acc_Z ** 2
        )


    if min_norm_value <= acc_Norm <= max_norm_value:
        result["AccNormValue"] = True
    else:
        result["AccNormValue"] = False

    if ((sensor_data.accX >= min_acc_X_value) & (sensor_data.accX <= max_acc_X_value)).all():
        result["AccXValue"] = True
    else:
        result["AccXValue"] = False

    if ((sensor_data.accY >= min_acc_Y_value) & (sensor_data.accY <= max_acc_Y_value)).all():
        result["AccYValue"] = True
    else:
        result["AccYValue"] = False

    if ((sensor_data.accZ >= min_acc_Z_value) & (sensor_data.accZ <= max_acc_Z_value)).all():
        result["AccZValue"] = True
    else:
        result["AccZValue"] = False 

    result["AccValue"] = result["AccXValue"] and result["AccYValue"] and result["AccZValue"]

    acc_X_20_sample = sensor_data.accX[:20]
    acc_Y_20_sample = sensor_data.accY[:20]
    acc_Z_20_sample = sensor_data.accZ[:20]

    Var_Acc_X = statistics.variance(acc_X_20_sample)
    Var_Acc_Y = statistics.variance(acc_Y_20_sample)
    Var_Acc_Z = statistics.variance(acc_Z_20_sample)

    if Var_Acc_X != 0 and 0 <= Var_Acc_X <= var_acc_value:
        result["AccXVar"] = True
    else:
        result["AccXVar"] = False

    if Var_Acc_Y != 0 and 0 <= Var_Acc_Y <= var_acc_value:
        result["AccYVar"] = True
    else:
        result["AccYVar"] = False

    if Var_Acc_Z != 0 and 0 <= Var_Acc_Z <= var_acc_value:
        result["AccZVar"] = True
    else:
        result["AccZVar"] = False

    result["AccVar"] = result["AccXVar"] and result["AccYVar"] and result["AccZVar"]

    result["AccResult"] = result["AccNormValue"] and result["AccValue"] and result["AccVar"]

    return result

def test_acc(dlg, base_path, acc_folder, max_norm_value, min_norm_value, min_acc_X_value, max_acc_X_value, min_acc_Y_value, max_acc_Y_value, min_acc_Z_value, max_acc_Z_value, var_acc_value, sleep_time):

    #print("Hard reset")

    time.sleep(2)

    log_acc_acilis = fnc.auto_start(dlg, base_path, acc_folder, sleep_time)
    

    try:
        sensor_data_acc_acilis = fnc.parse_log(log_acc_acilis)
    except (FileNotFoundError, ValueError) as e:
        return None
 
        
    results_calib_test = check_calibration_test(sensor_data_acc_acilis, max_norm_value, min_norm_value, min_acc_X_value, max_acc_X_value, min_acc_Y_value, max_acc_Y_value, min_acc_Z_value, max_acc_Z_value, var_acc_value)

<<<<<<< HEAD
    if results_calib_test["AccResult"] == True:
        print("Test 3: BAŞARILI")
    elif results_calib_test["AccResult"] == False:
        print("Test 3: BAŞARISIZ")
        if results_calib_test["AccNormValue"] == False:
            print("Acc Norm Hatalı")
        if results_calib_test["AccXValue"] == False:
            print("Acc X Değer Aralığı Yanlış")
        if results_calib_test["AccYValue"] == False:
            print("Acc Y Değer Aralığı Yanlış")
        if results_calib_test["AccZValue"] == False:
            print("Acc Z Değer Aralığı Yanlış")
        if results_calib_test["AccXVar"] == False:
            print("Acc Var X Değer Aralığı Yanlış")
        if results_calib_test["AccYVar"] == False:
            print("Acc Var Y Değer Aralığı Yanlış")
        if results_calib_test["AccZVar"] == False:
            print("Acc Var Z Değer Aralığı Yanlış")
        if results_calib_test["AccNormValue"] or results_calib_test["AccValue"] or results_calib_test["AccVar"]:
            print("BAŞARISIZ")

=======
>>>>>>> 61722c604d416dc33fed4d5583b26a493a8f5371
    return results_calib_test