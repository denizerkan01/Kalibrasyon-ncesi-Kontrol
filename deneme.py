import general_functions as fnc
import os
import glob

def all_same(items):
    return all(x == items[0] for x in items)

#C:\Users\Deniz Erkan\Desktop\KalibOncesiKontrol\UretimSonrasiTesti\M2GR\Gyro Elements Testi

def deneme(dlg, base_path, sub_folder):

    result = {
                        "GyroX_El": False,
                        "GyroY_El": False,
                        "GyroZ_El": False,
                        "Gyro_Success": False,
            }

    #log_gyro_el = fnc.auto_start(dlg, base_path, gyro_el_folder, sleep_time)

    target_folder = os.path.join(base_path, sub_folder),
    print(target_folder)
    
    log_file = glob.glob(os.path.join(target_folder, "log_*.txt"))
    print(log_file)
    """
    try:
        sensor_data_gyro_elements = fnc.parse_log(log_file)
    except (FileNotFoundError, ValueError) as e:
        return None
    
    gyro_X = sensor_data_gyro_elements.gyroX
    gyro_Y = sensor_data_gyro_elements.gyroY
    gyro_Z = sensor_data_gyro_elements.gyroZ
    
    result["GyroX_El"] = all_same(gyro_X)
    result["GyroY_El"] = all_same(gyro_Y)
    result["GyroZ_El"] = all_same(gyro_Z)
    
    result["Gyro_Success"] = result["GyroX_El"] and result["GyroY_El"] and result["GyroZ_El"]"""
    