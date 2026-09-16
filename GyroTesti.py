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
    }

    mean_gyro_X = np.mean(sensor_data.gyroX)
    mean_gyro_Y = np.mean(sensor_data.gyroY)
    mean_gyro_Z = np.mean(sensor_data.gyroZ)

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

    print("Hard reset")

    time.sleep(2)

    log_gyro_acilis = fnc.auto_start(dlg, base_path, gyro_folder, sleep_time)

    try:
        sensor_data_gyro_acilis = fnc.parse_log(log_gyro_acilis)
    except (FileNotFoundError, ValueError) as e:
        return None
     
            
    results_calib_test = check_calibration_test(sensor_data_gyro_acilis,  max_gyro_value, min_gyro_value, min_gyro_X_value, max_gyro_X_value, min_gyro_Y_value, max_gyro_Y_value, min_gyro_Z_value, max_gyro_Z_value, var_gyro_value)

    return results_calib_test