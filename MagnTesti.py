import time
import statistics
import numpy as np
import general_functions as fnc

def check_calibration_test(sensor_data, min_magn_norm, max_magn_norm, var_magn_value):

    result = {
                "MagnNormValue": False,
                "MagnXVar": False,
                "MagnYVar": False,
                "MagnZVar": False,
                "MagnVar": False,
                "MagnResult": False,

    }

    mean_magn_X = np.mean(sensor_data.magnX)
    mean_magn_Y = np.mean(sensor_data.magnY)
    mean_magn_Z = np.mean(sensor_data.magnZ)


    magn_Norm = np.sqrt(
                mean_magn_X ** 2 + 
                mean_magn_Y ** 2 + 
                mean_magn_Z ** 2
            )


    if min_magn_norm <= magn_Norm <= max_magn_norm:
        result["MagnNormValue"] = True
    else:
        result["MagnNormValue"] = False

    magn_X_20_sample = sensor_data.magnX[:20]
    magn_Y_20_sample = sensor_data.magnY[:20]
    magn_Z_20_sample = sensor_data.magnZ[:20]
    
    Var_Magn_X = statistics.variance(magn_X_20_sample)
    Var_Magn_Y = statistics.variance(magn_Y_20_sample)
    Var_Magn_Z = statistics.variance(magn_Z_20_sample)

    if Var_Magn_X != 0 and 0 <= Var_Magn_X <= var_magn_value:
        result["MagnXVar"] = True
    else:
        result["MagnXVar"] = False
    
    if Var_Magn_Y != 0 and 0 <= Var_Magn_Y <= var_magn_value:
        result["MagnYVar"] = True
    else:
        result["MagnYVar"] = False
    
    if Var_Magn_Z != 0 and 0 <= Var_Magn_Z <= var_magn_value:
        result["MagnZVar"] = True
    else:
        result["MagnZVar"] = False
    
    result["MagnVar"] = result["MagnXVar"] and result["MagnYVar"] and result["MagnZVar"]
    
    result["MagnResult"] = result["MagnNormValue"] and result["MagnVar"]
    
    return result

def test_magn(dlg, base_path, magn_folder, min_magn_norm, max_magn_norm, var_magn_value, sleep_time):

    #print("Hard reset")

    time.sleep(2)

    log_magn_acilis = fnc.auto_start(dlg, base_path, magn_folder, sleep_time)
    

    try:
        sensor_data_magn_acilis = fnc.parse_log(log_magn_acilis)
    except (FileNotFoundError, ValueError) as e:
        return None
 
        
    results_calib_test = check_calibration_test(sensor_data_magn_acilis, min_magn_norm, max_magn_norm, var_magn_value)

    if results_calib_test["MagnResult"] == True:
        print("Test 5: BAŞARILI")
    elif results_calib_test["MagnResult"] == False:
        print("Test 5: BAŞARISIZ")
        if results_calib_test["MagnNormValue"] == False:
            print("Magn Norm Hatalı")
        if results_calib_test["MagnXVar"] == False:
            print("Magn Var X Değer Aralığı Yanlış")
        if results_calib_test["MagnYVar"] == False:
            print("Magn Var Y Değer Aralığı Yanlış")
        if results_calib_test["MagnZVar"] == False:
            print("Magn Var Z Değer Aralığı Yanlış")
        if results_calib_test["MagnNormValue"] or results_calib_test["MagnVar"]:
            print("Test 5: BAŞARISIZ")

    return results_calib_test