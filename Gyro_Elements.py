import time
import general_functions as fnc
import numpy as np



"""def any_same(sensor_data):

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
    gyro_Y = sensor_data_gyro_elements.gyroY
    gyro_Z = sensor_data_gyro_elements.gyroZ

    result_gyroX = any_same(gyro_X)
    result_gyroY = any_same(gyro_Y)
    result_gyroZ = any_same(gyro_Z)

    result["GyroX_El"] = result_gyroX["has_duplicates"]
    result["GyroY_El"] = result_gyroY["has_duplicates"]
    result["GyroZ_El"] = result_gyroZ["has_duplicates"]


    result["Gyro_Success"] = result["GyroX_El"] and result["GyroY_El"] and result["GyroZ_El"]

    if result["Gyro_Success"] == False:
        print("Test 7: BAŞARILI")
    elif result["Gyro_Success"] == True:
        print("Test 7: BAŞARISIZ")
        if result["GyroX_El"] == True:
            print("Gyro X'de aynı veri gözlemlenen satırlar:", result_gyroX["row"])
        if result["GyroY_El"] == True:
            print("Gyro Y'de aynı veri gözlemlenen satırlar:", result_gyroY["row"])
        if result["GyroZ_El"] == True:
            print("Gyro Z'de aynı veri gözlemlenen satırlar:", result_gyroZ["row"])




    return result"""






def any_same_consecutive(sensor_data, min_run=3):

    data = np.asarray(sensor_data)
    result = {"has_duplicates": False, "runs": [], "row": []}

    if data.size < min_run:
        return result

    same = data[1:] == data[:-1]            
    padded = np.concatenate(([False], same, [False])).astype(int)
    edges = np.diff(padded)
    starts = np.where(edges == 1)[0]        
    ends = np.where(edges == -1)[0]          
    lengths = ends - starts + 1

    for s, e, n in zip(starts, ends, lengths):
        if n >= min_run:
            result["runs"].append({
                "start_row": int(s) + 1,
                "end_row": int(e) + 1,
                "value": data[s].item(),
                "length": int(n),
            })

    result["has_duplicates"] = len(result["runs"]) > 0
    result["row"] = [f"{r['start_row']}-{r['end_row']}" for r in result["runs"]]
    return result


def Gyro_Elements(dlg, base_path, gyro_el_folder, sleep_time, settle_time=2, min_run=3):
    time.sleep(settle_time)
    log_file = fnc.auto_start(dlg, base_path, gyro_el_folder, sleep_time)
    print("Log File:", log_file)

    try:
        data = fnc.parse_log(log_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Test 7: log okunamadı -> {e}")
        return None

    axis_results = {
        "X": any_same_consecutive(data.gyroX, min_run),
        "Y": any_same_consecutive(data.gyroY, min_run),
        "Z": any_same_consecutive(data.gyroZ, min_run),
    }

    result = {f"Gyro{ax}_El": r["has_duplicates"] for ax, r in axis_results.items()}
    result["Gyro_Success"] = any(result.values())  

    if not result["Gyro_Success"]:
        print("Test 7: BAŞARILI")
    else:
        print("Test 7: BAŞARISIZ")
        for ax, r in axis_results.items():
            for run in r["runs"]:
                print(f"Gyro {ax}: satır {run['start_row']}-{run['end_row']} "
                      f"arası aynı veri ({run['value']}), {run['length']} adet")

    return result