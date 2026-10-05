import time
import general_functions as fnc
import numpy as np


def any_same(sensor_data):

    #Aynı data bulunca True return eder
    #False result data sette aynı veri yok demek

    result = {
                "has_duplicates": False,
                "row": [],

    }

    sensor_data = np.asarray(sensor_data)

    values, counts = np.unique(sensor_data, return_counts=True)
    duplicates = values[counts > 1]
    has_duplicates = len(duplicates) > 0
    result["has_duplicates"] = has_duplicates

    if has_duplicates:
        for v in duplicates:
            rows = np.where(sensor_data == v)[0] + 1   
            result["row"] = rows

    return result



def Gyro_Elements(dlg, base_path, gyro_el_folder, sleep_time):

    result = {
                    "GyroX_El": False,
                    "GyroY_El": False,
                    "GyroZ_El": False,
                    "Gyro_Success": False,
        }

    time.sleep(2)
    
    log_gyro_el = fnc.auto_start(dlg, base_path, gyro_el_folder, sleep_time)

    print("Log File:", log_gyro_el)
    
    try:
        sensor_data_gyro_elements = fnc.parse_log(log_gyro_el)
    except (FileNotFoundError, ValueError) as e:
        return None
    
    gyro_X = sensor_data_gyro_elements.gyroX
    print("Gyro X", gyro_X[1])
    gyro_Y = sensor_data_gyro_elements.gyroY
    print("Gyro Y", gyro_Y[1])
    gyro_Z = sensor_data_gyro_elements.gyroZ
    print("Gyro Z", gyro_Z[1])

    result_gyroX = any_same(gyro_X)
    result_gyroY = any_same(gyro_Y)
    result_gyroZ = any_same(gyro_Z)

    result["GyroX_El"] = result_gyroX["has_duplicates"]
    result["GyroY_El"] = result_gyroY["has_duplicates"]
    result["GyroZ_El"] = result_gyroZ["has_duplicates"]


    result["Gyro_Success"] = result["GyroX_El"] and result["GyroY_El"] and result["GyroZ_El"]

    if result["Gyro_Success"] == False:
        print("Test 6: BAŞARILI")
    elif result["Gyro_Success"] == True:
        print("Test 6: BAŞARISIZ")
        if result["GyroX_El"] == True:
            print("Gyro X'de aynı veri gözlemlenen satırlar:", result_gyroX["row"])
        if result["GyroY_El"] == True:
            print("Gyro Y'de aynı veri gözlemlenen satırlar:", result_gyroY["row"])
        if result["GyroZ_El"] == True:
            print("Gyro Z'de aynı veri gözlemlenen satırlar:", result_gyroZ["row"])




    return result



    