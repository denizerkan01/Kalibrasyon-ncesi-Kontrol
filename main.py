import os
import sys
import glob
import time
import pyperclip
import serial.tools.list_ports
import general_functions as fnc
from types import SimpleNamespace

import numpy as np


from pywinauto.keyboard import send_keys
from pywinauto.application import Application
import SN_Yukleme as SN_Yukleme
import AccTesti as AccTesti
import GyroTesti as GyroTesti
import MagnTesti as MagnTesti
import KalibIdentityTesti as KalibIdentityTesti
import UartRs232Testi as UartRs232Testi

import Gyro_Elements as Gyro_Elements

import Sonuc as Sonuc

from pywinauto import mouse

"""import ctypes, sys

if not ctypes.windll.shell32.IsUserAnAdmin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(f'"{a}"' for a in sys.argv), None, 1
    )
    sys.exit()"""


#Çalıştırılan dosya konumu bulunur
path_arview = r"C:\Program Files\ArView\ArView.exe"
base_path = os.path.dirname(os.path.abspath(__file__)) 
print(base_path)
active_dlg = None

def open_data_select(dlg, checkbox_states):

    dlg.child_window(title="Data Select", control_type="Button").click_input()
    
    for name, desired in checkbox_states:
        checkbox = dlg.child_window(title=name, control_type="CheckBox")
        state = checkbox.get_toggle_state()
        if state != desired:
            checkbox.click_input()

    dlg.child_window(title="Save", control_type="Pane", found_index=0).click_input()

def create_folder(base_path):

    relative_paths = [
        "Device",
        "Test Sonuclari",
        os.path.join("UretimSonrasiTesti", "S3A", "Kalibrasyon Matris Testi"),
        os.path.join("UretimSonrasiTesti", "S3A", "FW Testi"),
        os.path.join("UretimSonrasiTesti", "S3A", "Acc Testi"),
        os.path.join("UretimSonrasiTesti", "S3A", "Gyro Testi"),
        os.path.join("UretimSonrasiTesti", "S3A", "Gyro Elements Testi"),
        os.path.join("UretimSonrasiTesti", "S3A", "Magn Testi"),
        os.path.join("UretimSonrasiTesti", "S3A", "Uart RS 232 Testi"),
    ]

    relative_paths_m2_gr = [
            "Device",
            "Test Sonuclari",
            os.path.join("UretimSonrasiTesti", "M2GR", "Kalibrasyon Matris Testi"),
            os.path.join("UretimSonrasiTesti", "M2GR", "FW Testi"),
            os.path.join("UretimSonrasiTesti", "M2GR", "Acc Testi"),
            os.path.join("UretimSonrasiTesti", "M2GR", "Gyro Testi"),
            os.path.join("UretimSonrasiTesti", "M2GR", "Gyro Elements Testi"),
            os.path.join("UretimSonrasiTesti", "M2GR", "Magn Testi"),
            os.path.join("UretimSonrasiTesti", "M2GR", "Uart RS 232 Testi"),
        ]

    for rel_path in relative_paths:
        full_path = os.path.join(base_path, rel_path)
        os.makedirs(full_path, exist_ok=True)

    for rel_path_m2_gr in relative_paths_m2_gr:
        full_path_m2_gr = os.path.join(base_path, rel_path_m2_gr)
        os.makedirs(full_path_m2_gr, exist_ok=True)

def find_limit_file(pn_dvc, file_path):

    limit_file_path = os.path.join(file_path, "Limit Dosyaları")
    limit_file_path = os.path.join(limit_file_path, f"{pn_dvc}_limitdegerleri_v00.txt")
    s3a_limitdegerleri_v00 = {}

    with open(limit_file_path, "r", encoding="utf-8") as file:
        exec(file.read(), {}, s3a_limitdegerleri_v00) 

    return s3a_limitdegerleri_v00

def find_limit_file_m2_gr(pn_dvc, file_path):

    limit_file_path_m2_gr = os.path.join(file_path, "Limit Dosyaları")
    limit_file_path_m2_gr = os.path.join(limit_file_path_m2_gr, f"{pn_dvc}_limitdegerleri_v00.txt")
    m2_gr_limitdegerleri_v00 = {}

    with open(limit_file_path_m2_gr, "r", encoding="utf-8") as file:
        exec(file.read(), {}, m2_gr_limitdegerleri_v00) 

    return m2_gr_limitdegerleri_v00

def find_gyro_config_0_file_s3a(file_path):

    config_file_path = os.path.join(file_path, "Limit Dosyaları")
    config_file_path = os.path.join(config_file_path, "S3A_mag_0.txt")
    s3a_config_0 = {}

    with open(config_file_path, "r", encoding="utf-8") as file:
        exec(file.read(), {}, s3a_config_0) 

    return s3a_config_0

def find_sn_file(file_path):
    limit_file_sn = os.path.join(file_path, "Limit Dosyaları", "SN_Takip.txt")

    with open(limit_file_sn, "r", encoding="utf-8") as file:
        sn = file.read().strip()

    return sn  # "00000001" (string olarak döner, baştaki sıfırlar korunur)

def load_sn_m2_gr(pn_dvc, file_path):


    limit_file_path = os.path.join(file_path, "Limit Dosyaları", f"{pn_dvc}_SN.txt")

    with open(limit_file_path, "r", encoding="utf-8") as file:
        sn = file.read().strip()

    return sn         

def launch_arview(path):
    global active_dlg
    app = Application(backend="uia").start(path, work_dir=os.path.dirname(path))
    dlg = app.window(auto_id="FormMain", control_type="Window")
    dlg.wait("visible ready", timeout=60)
    active_dlg = dlg
    return dlg

def device_sn(device_folder):
    dlg = launch_arview(path_arview) 
    time.sleep(5)

    ports = list(serial.tools.list_ports.comports())
    
    target_standard = fnc.find_port("Standard", ports)

    if not fnc.try_connect(dlg, target_standard, "Standard"):
        print("GUI_INFO|custom|Sisteme bağlanılamamaktadır.")
        sys.exit("!!! Can't Connect to the Device !!!")

    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    dlg.child_window(title="Copy to Clipboard", control_type="Pane").click_input()
    time.sleep(5)
    send_keys("%{F4}")
    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    time.sleep(5)
    send_keys("%{F4}")

    devicesn_folder = os.path.join(base_path, device_folder)

    config_path = os.path.join(devicesn_folder, "config.txt")
    clipboard_content = pyperclip.paste()
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(clipboard_content)


    with open(config_path, 'r') as file:
        for line in file:
            if line.startswith('DeviceSN'):
                return line.split('=', 1)[1].strip().strip('"')
    return None

"""def save_sn_file(file_path, sn):
    limit_file_sn = os.path.join(file_path, "Limit Dosyaları", "SN_Takip.txt")
    with open(limit_file_sn, "w", encoding="utf-8") as file:
        file.write(sn)"""

def device_pn(device_folder):

    dlg = launch_arview(path_arview) 
    time.sleep(5)

    ports = list(serial.tools.list_ports.comports())
    
    target_standard = fnc.find_port("Standard", ports)
    
    if fnc.try_connect(dlg, target_standard, "Standard"):
        print("Connect device with Standard Port")

    else:
        sys.exit("!!! Can't Connect to the Device !!!")


    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    dlg.child_window(title="Copy to Clipboard", control_type="Pane").click_input()
    time.sleep(5)
    send_keys("%{F4}")
    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    time.sleep(5)
    send_keys("%{F4}")

    device_info_folder = os.path.join(base_path, device_folder)

    config_path = os.path.join(device_info_folder, "config.txt")
    clipboard_content = pyperclip.paste()
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(clipboard_content)

    with open(config_path, 'r') as file:
        for line in file:
            if line.startswith('DevicePN'):
                return line.split('=', 1)[1].strip().strip('"')
    return None


def main():

    fnc.check_stop_requested()

    create_folder(base_path)

    device_folder_name = "Device"

    

    sn_dvc = device_sn(device_folder_name)
    print("@@SERIAL_NUMBER:" + str(sn_dvc), flush=True)
    pn_dvc = device_pn(device_folder_name)
    print("@@PART_NUMBER:" + str(pn_dvc), flush=True)

    fnc.check_stop_requested()

    print("PN:", pn_dvc)

    print(f"pn_dvc (raw) = {pn_dvc!r}")   # debug: remove once resolved
    pn_dvc = str(pn_dvc).strip().upper()

    if pn_dvc == "M2GR051433A":
        limit_data_m2_gr = find_limit_file_m2_gr(pn_dvc, base_path)
        limits = SimpleNamespace(**limit_data_m2_gr)
        print("M2 sistemi kullanılıyor")
        hw_ver = limits.hw_ver
        device_name = limits.device_name
        print("M2 HW:", hw_ver)
    elif pn_dvc == "S3A097190":
        limit_data = find_limit_file(pn_dvc, base_path)
        limits = SimpleNamespace(**limit_data)
        gyro_data_0 = find_gyro_config_0_file_s3a(base_path)
        config_0 = gyro_data_0["CalibMag"]
        print("Config 0:", config_0)
        print("S3A sistemi kullanılıyor")
        hw_ver = limits.hw_ver
        device_name = limits.device_name
        print("S3A HW:", hw_ver)

    else:
        # Fail early with a clear message instead of UnboundLocalError later
        raise ValueError(f"Desteklenmeyen part number: {pn_dvc!r}")

    
    time.sleep(3)
    fnc.check_stop_requested()

    dlg = launch_arview(path_arview) 

    print("SN:",sn_dvc)

    #device_name = limits.device_name

    #sn_load = load_sn_m2_gr(pn_dvc, base_path)
    #print("SN:", sn_load)

    file_sn = find_sn_file(base_path)
    
    print("Dosyadan okunan SN:",file_sn)

    dvc = SN_Yukleme.SN_Yukleme(dlg,sn_dvc, base_path, hw_ver, pn_dvc, device_name, file_sn)
    print("DVC:",dvc)

    #next_sn = str(int(file_sn) + 1).zfill(len(file_sn))
    #print("Yeni SN:", next_sn)

    #save_sn_file(base_path, next_sn)

    #dlg.child_window(title="Disconnect", control_type="Button").click_input()
    #time.sleep(5)
    send_keys("%{F4}")


    dlg = launch_arview(limits.arview_path) 
    
    ports = list(serial.tools.list_ports.comports())
    
    target_standard = fnc.find_port("Standard", ports)

    if not fnc.try_connect(dlg, target_standard, "Standard"):
        sys.exit("!!! Can't Connect to the Device !!!")

    #dlg.print_control_identifiers(filename="tree4.txt")

    uretim_folder_path = os.path.join(base_path, r"UretimSonrasiTesti")

    if pn_dvc == "M2GR051433A":
        folder_path = os.path.join(uretim_folder_path, r"M2GR")
    elif pn_dvc == "S3A097190":
        folder_path = os.path.join(uretim_folder_path, r"S3A")


    open_data_select(dlg, limits.checkbox_states_general)
    fnc.check_stop_requested()

    #Test 1: Tüm Kalibrasyon Matrisleri Identity mi?
    print("@@PHASE:1,2", flush=True)
    
    print("***Test 1 - Kalibrasyon Matris Kontrol Testi Sonucu:")

    results_Kalibrasyon_Kontrol = KalibIdentityTesti.KalibIdentityTesti(dlg, folder_path, limits.kalibrasyon_kontrol_folder, limits.ref_matrix_acc, limits.firmware_version)
    fnc.check_stop_requested()
    print("@@RESULT:1:" + ("PASS" if results_Kalibrasyon_Kontrol["calib_ctrl_success"] == True else "FAIL"), flush=True)
    print("@@RESULT:2:" + ("PASS" if results_Kalibrasyon_Kontrol["firmware_version_match"] == True else "FAIL"), flush=True)


    if results_Kalibrasyon_Kontrol["calib_ctrl_success"] == True:
        print("Test 1: BAŞARILI")
    else:
        print("Test 1: BAŞARISIZ")
        if results_Kalibrasyon_Kontrol["acc_is_calibrated"] == False:
            print("Sistemde Acc kalibrasyonu bulunmaktadır")

        if results_Kalibrasyon_Kontrol["gyro_is_calibrated"] == False:
            print("Sistemde Gyro kalibrasyonu bulunmaktadır")

        if results_Kalibrasyon_Kontrol["magn_is_calibrated"] == False:
            print("Sistemde Magn kalibrasyonu bulunmaktadır")

        if results_Kalibrasyon_Kontrol["acc_is_calibrated"] == False or results_Kalibrasyon_Kontrol["gyro_is_calibrated"] == False or results_Kalibrasyon_Kontrol["magn_is_calibrated"] == False:
            sys.exit("Kalibrasyon matrislerini initial hale getiriniz.")
    
    print("***Test 2 - FW Versiyon Kontrol Testi Sonucu:")

    if results_Kalibrasyon_Kontrol["firmware_version_match"] == True:
        print("Test 2: BAŞARILI")
    elif results_Kalibrasyon_Kontrol["firmware_version_match"] == False:
        print("Test 2: BAŞARISIZ")
    
    print("***Test 3 - Acc Kontrol Testi Sonucu:")
    print("@@PHASE:3", flush=True)

    acilis_folder_acc = fnc.navigate_to_folder(dlg, folder_path, limits.acc_folder)
    results_Acc_Acilis = AccTesti.test_acc(dlg, folder_path, acilis_folder_acc,  limits.max_norm_value, limits.min_norm_value, limits.min_acc_X_value, limits.max_acc_X_value, limits.min_acc_Y_value, limits.max_acc_Y_value, limits.min_acc_Z_value, limits.max_acc_Z_value, limits.var_acc_value, limits.sleep_time_acc)
    print("@@RESULT:3:" + ("PASS" if results_Acc_Acilis is not None and results_Acc_Acilis.get("AccResult") == True else "FAIL"), flush=True)
    fnc.check_stop_requested()
    
    print("***Test 4 - Gyro Kontrol Testi Sonucu:")
    print("@@PHASE:4", flush=True)

    acilis_folder_gyro = fnc.navigate_to_folder(dlg, folder_path, limits.gyro_folder)
    results_Gyro_Acilis = GyroTesti.test_gyro(dlg, folder_path, acilis_folder_gyro,  limits.max_gyro_value, limits.min_gyro_value, limits.min_gyro_X_value, limits.max_gyro_X_value, limits.min_gyro_Y_value, limits.max_gyro_Y_value, limits.min_gyro_Z_value, limits.max_gyro_Z_value, limits.var_gyro_value, limits.sleep_time_gyro)
    print("@@RESULT:4:" + ("PASS" if results_Gyro_Acilis is not None and results_Gyro_Acilis.get("GyroResult") == True else "FAIL"), flush=True)
    fnc.check_stop_requested()
    
    print("***Test 5 - Magn Kontrol Testi Sonucu:")
    print("@@PHASE:5", flush=True)

    acilis_folder_magn = fnc.navigate_to_folder(dlg, folder_path, limits.magn_folder)     
    results_Magn = MagnTesti.test_magn(dlg, folder_path, acilis_folder_magn,  limits.min_magn_norm, limits.max_magn_norm, limits.var_magn_value, limits.sleep_time_gyro)
    print("@@RESULT:5:" + ("PASS" if results_Magn is not None and results_Magn.get("MagnResult") == True else "FAIL"), flush=True)
    fnc.check_stop_requested()
    
    print("Test 6 - UART Testi Sonucu:")
    print("@@PHASE:6", flush=True)
    
    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    

    result_uart = UartRs232Testi.UartRs232Testi(dlg, folder_path, limits.kalibrasyon_kontrol_folder, limits.ref_matrix_acc, limits.firmware_version)
    print("@@RESULT:6:" + ("PASS" if result_uart is not None and result_uart.get("Conn_Result") is True else "FAIL"), flush=True)
    fnc.check_stop_requested()

    if not fnc.try_connect(dlg, target_standard, "Standard"):
        sys.exit("!!! Can't Connect to the Device !!!")

    #calibMag [all zero]
    #dlg.print_control_identifiers(filename="tree4.txt")

    #
    print("Test 7 - Gyro Testi Sonucu:")
    print("@@PHASE:7", flush=True)

    if pn_dvc == "M2GR051433A":
        print("M2")
        fnc.target_meas(dlg, limits.checkbox_states_target_meas_gyroz_testi)
            
    elif pn_dvc == "S3A097190":

        dlg.child_window(title="Settings", control_type="Button").click_input()

        r = dlg.rectangle()
        mouse.scroll(coords=(r.mid_point().x, r.mid_point().y), wheel_dist=-5)  

        dlg.child_window(title="Magnetometer Calibration", control_type="ListItem").double_click_input()


        item = dlg.child_window(title="Magnetometer Calibration", control_type="ListItem")
        value = item.children()[1]        
        value.click_input()

        send_keys("^a{DEL}")

        config_0 = "[" + ",".join(str(x) for x in limits.magn_config_0) + "]"

        send_keys(config_0, with_spaces=True)
        time.sleep(3)

        dlg.child_window(title="OK", auto_id="buttonOK", control_type="Pane").click_input()
        dlg.child_window(title="Save", auto_id="buttonSave", control_type="Pane").click_input()

        time.sleep(3)
        send_keys("%{F4}")

        time.sleep(2)

        dlg.child_window(title="Console", control_type="Button").click_input()
        
        time.sleep(3)
        
        dlg.child_window(title="Reset", control_type="Pane").click_input()

    acilis_folder_gyro_el = fnc.navigate_to_folder(dlg, folder_path, limits.gyro_el_folder)
    #result_Gyro_El = Gyro_Elements.Gyro_Elements(dlg, folder_path, limits.gyro_el_folder, limits.sleep_time_gyro_el)
    result_Gyro_El = Gyro_Elements.Gyro_Elements(dlg, folder_path, limits.gyro_el_folder, limits.sleep_time_gyro_el, settle_time=2, min_run=3)
    print("@@RESULT:7:" + ("PASS" if result_Gyro_El is not None and result_Gyro_El.get("Gyro_Success") == False else "FAIL"), flush=True)
    fnc.check_stop_requested()
    print("@@PHASE:DONE", flush=True)

    if pn_dvc == "M2GR051433A":
        print("M2")
        fnc.target_meas(dlg, limits.checkbox_states_target_meas_gyroz_testi_m2gr)
        
                
    elif pn_dvc == "S3A097190":
        dlg.child_window(title="Settings", control_type="Button").click_input()
        
        r = dlg.rectangle()
        mouse.scroll(coords=(r.mid_point().x, r.mid_point().y), wheel_dist=-5)  
        
        dlg.child_window(title="Magnetometer Calibration", control_type="ListItem").double_click_input()
        
        item = dlg.child_window(title="Magnetometer Calibration", control_type="ListItem")
        value = item.children()[1]        
        value.click_input()
        
        send_keys("^a{DEL}")
        
        config_1 = "[" + ",".join(str(x) for x in limits.magn_config_1) + "]"
        
        send_keys(config_1, with_spaces=True)
        time.sleep(3)
        
        dlg.child_window(title="OK", auto_id="buttonOK", control_type="Pane").click_input()
        dlg.child_window(title="Save", auto_id="buttonSave", control_type="Pane").click_input()
        
        time.sleep(3)
        send_keys("%{F4}")
        
        time.sleep(3)
                        
        dlg.child_window(title="Reset", control_type="Pane").click_input()
        
        dlg.child_window(title="Console", control_type="Button").click_input()
                
        

    
    

    dlg.child_window(title="Disconnect", control_type="Button").click_input()

    time.sleep(5)
    send_keys("%{F4}")
    send_keys("%{F4}")

    Sonuc.Sonuc(pn_dvc, dvc, base_path, results_Kalibrasyon_Kontrol, results_Acc_Acilis, results_Gyro_Acilis, results_Magn, result_uart, result_Gyro_El)


"""def main():
    try:
        main()
    except fnc.StopRequested:
        print("Test durdurma isteği alındı. Güvenli durdurma tamamlandı.")
    finally:
        if active_dlg is not None:
            try:
                disconnect = active_dlg.child_window(title="Disconnect", control_type="Button")
                if disconnect.exists(timeout=0.5):
                    disconnect.click_input()
            except Exception:
                pass
            try:
                if active_dlg.exists():
                    active_dlg.close()
            except Exception:
                pass"""
    





if __name__ == "__main__":
    main()








