import os
import sys
import time
import pyperclip
import serial.tools.list_ports
import general_functions as fnc
from types import SimpleNamespace

from pywinauto.keyboard import send_keys
from pywinauto.application import Application
import AccTesti as AccTesti
import GyroTesti as GyroTesti
import MagnTesti as MagnTesti
import KalibIdentityTesti as KalibIdentityTesti
import DataSelectTesti as DataSelectTesti

#Çalıştırılan dosya konumu bulunur
path_arview = r"C:\Program Files\ArView\ArView.exe"
base_path = os.path.dirname(os.path.abspath(__file__)) 

def create_folder(base_path):

    relative_paths = [
        "Device",
        os.path.join("UretimSonrasiTesti", "S3A", "Kalibrasyon Matris Testi"),
        os.path.join("UretimSonrasiTesti", "S3A", "FW Testi"),
        os.path.join("UretimSonrasiTesti", "S3A", "Acc Testi"),
        os.path.join("UretimSonrasiTesti", "S3A", "Gyro Testi"),
        os.path.join("UretimSonrasiTesti", "S3A", "Magn Testi"),
        os.path.join("UretimSonrasiTesti", "S3A", "Uart RS 232 Testi"),
    ]

    for rel_path in relative_paths:
        full_path = os.path.join(base_path, rel_path)
        os.makedirs(full_path, exist_ok=True)

def find_limit_file(pn_dvc, file_path):

    limit_file_path = os.path.join(file_path, "Limit Dosyaları")
    limit_file_path = os.path.join(limit_file_path, f"{pn_dvc}_limitdegerleri_v00.txt")
    s3a_limitdegerleri_v00 = {}

    with open(limit_file_path, "r", encoding="utf-8") as file:
        exec(file.read(), {}, s3a_limitdegerleri_v00) 

    return s3a_limitdegerleri_v00

def launch_arview(path):
    app = Application(backend="uia").start(path)
    dlg = app.window(auto_id="FormMain", control_type="Window")
    dlg.wait("visible ready", timeout=60)
    return dlg

def device_pn(device_folder):

    dlg = launch_arview(path_arview) 
    time.sleep(5)

    ports = list(serial.tools.list_ports.comports())
    
    target_standard = fnc.find_port("Standard", ports)
    #target_standard = fnc.find_port("Enhanced", ports)
    
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

def open_data_select(dlg, checkbox_states):

    dlg.child_window(title="Data Select", control_type="Button").click_input()
    
    for name, desired in checkbox_states:
        checkbox = dlg.child_window(title=name, control_type="CheckBox")
        state = checkbox.get_toggle_state()
        if state != desired:
            checkbox.click_input()

    dlg.child_window(title="Save", control_type="Pane", found_index=0).click_input()

def main():

    create_folder(base_path)

    device_folder_name = "Device"

    #
    pn_dvc = device_pn(device_folder_name)

    limit_data = find_limit_file(pn_dvc, base_path)
    limits = SimpleNamespace(**limit_data)
    
    time.sleep(5)

    dlg = launch_arview(limits.arview_path) 
    
    ports = list(serial.tools.list_ports.comports())
    
    target_standard = fnc.find_port("Standard", ports)

    if not fnc.try_connect(dlg, target_standard, "Standard"):
        sys.exit("!!! Can't Connect to the Device !!!")

    uretim_folder_path = os.path.join(base_path, r"UretimSonrasiTesti")
    s3a_folder_path = os.path.join(uretim_folder_path, r"S3A")

    open_data_select(dlg, limits.checkbox_states_general)

    #Test 1: Tüm Kalibrasyon Matrisleri Identity mi?

    #print("***Test 1 - Kalibrasyon Matris Kontrol Testi Sonucu:")

    results_Kalibrasyon_Kontrol = KalibIdentityTesti.KalibIdentityTesti(dlg, s3a_folder_path, limits.kalibrasyon_kontrol_folder, limits.ref_matrix, limits.firmware_version)

    if results_Kalibrasyon_Kontrol["calib_ctrl_success"] == True:
        #print("Sistemde yüklü kalibrasyon yoktur.")
        print("Test 1: BAŞARILI")
    else:
        print("Test 1: BAŞARISIZ")
        if results_Kalibrasyon_Kontrol["acc_is_calibrated"] == False:
            print("--Acc")

        if results_Kalibrasyon_Kontrol["gyro_is_calibrated"] == False:
            print("--Gyro")

        if results_Kalibrasyon_Kontrol["magn_is_calibrated"] == False:
            print("--Magn")

        if results_Kalibrasyon_Kontrol["acc_is_calibrated"] == False or results_Kalibrasyon_Kontrol["gyro_is_calibrated"] == False or results_Kalibrasyon_Kontrol["magn_is_calibrated"] == False:
            sys.exit("Kalibrasyon matrislerini initial hale getiriniz.")

    #print("***Test 2 - FW Versiyon Kontrol Testi Sonucu:")

    if results_Kalibrasyon_Kontrol["firmware_version_match"] == True:
        print("Test 2: BAŞARILI")
        #print("Sistemde bulunan FW doğrudur.")
    elif results_Kalibrasyon_Kontrol["firmware_version_match"] == False:
        print("Test 2: BAŞARISIZ")
        sys.exit("Sistemde bulunan FW yanlıştır. 00A000000001000A yüklü olması beklenmektedir.")

    #print("***Test 3 - Acc Kontrol Testi Sonucu:")
    acilis_folder_acc = fnc.navigate_to_folder(dlg, s3a_folder_path, limits.acc_folder)

    results_Acc_Acilis = AccTesti.test_acc(dlg, s3a_folder_path, acilis_folder_acc,  limits.max_norm_value, limits.min_norm_value, limits.min_acc_X_value, limits.max_acc_X_value, limits.min_acc_Y_value, limits.max_acc_Y_value, limits.min_acc_Z_value, limits.max_acc_Z_value, limits.var_acc_value, limits.sleep_time_acc)
    if results_Acc_Acilis["AccResult"] == True:
        print("Test 3: BAŞARILI")
    elif results_Acc_Acilis["AccResult"] == False:
        if results_Acc_Acilis["AccNormValue"] == False:
            print("Acc Norm Hatalı")
        if results_Acc_Acilis["AccXValue"] == False:
            print("Acc X Değer Aralığı Yanlış")
        if results_Acc_Acilis["AccYValue"] == False:
            print("Acc Y Değer Aralığı Yanlış")
        if results_Acc_Acilis["AccZValue"] == False:
            print("Acc Z Değer Aralığı Yanlış")
        if results_Acc_Acilis["AccXVar"] == False:
            print("Acc Var X Değer Aralığı Yanlış")
        if results_Acc_Acilis["AccYVar"] == False:
            print("Acc Var Y Değer Aralığı Yanlış")
        if results_Acc_Acilis["AccZVar"] == False:
            print("Acc Var Z Değer Aralığı Yanlış")
        if results_Acc_Acilis["AccNormValue"] or results_Acc_Acilis["AccValue"] or results_Acc_Acilis["AccVar"]:
            sys.exit("Test 3: BAŞARISIZ")

    #print("***Test 4 - Gyro Kontrol Testi Sonucu:")

    acilis_folder_gyro = fnc.navigate_to_folder(dlg, s3a_folder_path, limits.gyro_folder)
    
    results_Gyro_Acilis = GyroTesti.test_gyro(dlg, s3a_folder_path, acilis_folder_gyro,  limits.max_gyro_value, limits.min_gyro_value, limits.min_gyro_X_value, limits.max_gyro_X_value, limits.min_gyro_Y_value, limits.max_gyro_Y_value, limits.min_gyro_Z_value, limits.max_gyro_Z_value, limits.var_gyro_value, limits.sleep_time_gyro)
        
    if results_Gyro_Acilis["GyroResult"] == True:
        print("Test 4: BAŞARILI")
    elif results_Gyro_Acilis["GyroResult"] == False:
        if results_Gyro_Acilis["GyroNormValue"] == False:
            print("Gyro Norm Hatalı")
        if results_Gyro_Acilis["GyroXValue"] == False:
            print("Gyro X Değer Aralığı Yanlış")
        if results_Gyro_Acilis["GyroYValue"] == False:
            print("Gyro Y Değer Aralığı Yanlış")
        if results_Gyro_Acilis["GyroZValue"] == False:
            print("Gyro Z Değer Aralığı Yanlış")
        if results_Gyro_Acilis["GyroXVar"] == False:
            print("Gyro Var X Değer Aralığı Yanlış")
        if results_Gyro_Acilis["GyroYVar"] == False:
            print("Gyro Var Y Değer Aralığı Yanlış")
        if results_Gyro_Acilis["GyroZVar"] == False:
            print("Gyro Var Z Değer Aralığı Yanlış")
        if results_Gyro_Acilis["GyroNormValue"] or results_Gyro_Acilis["GyroValue"] or results_Gyro_Acilis["GyroVar"]:
            sys.exit("Test 4: BAŞARISIZ")


    #print("***Test 5 - Magn Kontrol Testi Sonucu:")
    
    acilis_folder_magn = fnc.navigate_to_folder(dlg, s3a_folder_path, limits.magn_folder)
        
    results_Magn = MagnTesti.test_magn(dlg, s3a_folder_path, acilis_folder_magn,  limits.min_magn_norm, limits.max_magn_norm, limits.var_magn_value, limits.sleep_time_gyro)

    if results_Magn["MagnResult"] == True:
        print("Test 5: BAŞARILI")
    elif results_Magn["MagnResult"] == False:
        if results_Magn["MagnNormValue"] == False:
            print("Magn Norm Hatalı")
        if results_Magn["MagnXVar"] == False:
            print("Magn Var X Değer Aralığı Yanlış")
        if results_Magn["MagnYVar"] == False:
            print("Magn Var Y Değer Aralığı Yanlış")
        if results_Magn["MagnZVar"] == False:
            print("Magn Var Z Değer Aralığı Yanlış")
        if results_Magn["MagnNormValue"] or results_Magn["MagnVar"]:
            sys.exit("Test 5: BAŞARISIZ")

    #print("Test 6 - UART Testi Sonucu:")
    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    
    ports = list(serial.tools.list_ports.comports())
    target_enhanced = fnc.find_port("Enhanced", ports)
    target_standard = fnc.find_port("Standard", ports)

    result_UART = False
    
    if fnc.try_connect(dlg, target_enhanced, "Enhanced"):
        results_uart_conn = KalibIdentityTesti.KalibIdentityTesti(dlg, s3a_folder_path, limits.kalibrasyon_kontrol_folder, limits.ref_matrix, limits.firmware_version)
        if results_uart_conn["firmware_version_match"] == True:
            result_UART = True
        else:
            result_UART = False

    dlg.child_window(title="Disconnect", control_type="Button").click_input()
    
    if fnc.try_connect(dlg, target_standard, "Standard"):
        results_232_conn = KalibIdentityTesti.KalibIdentityTesti(dlg, s3a_folder_path, limits.kalibrasyon_kontrol_folder, limits.ref_matrix, limits.firmware_version)
        if results_232_conn["firmware_version_match"] == True:
            result_232 = True
        else:
            result_232 = False

    result_conn = result_UART and result_232

    if result_conn == True:
        print("Test 6: BAŞARILI")
    else:
        if result_UART == False:
            print("UART ile Bağlanılamadı")
        if result_232 == False:
                    print("RS232 ile Bağlanılamadı")

    dlg.child_window(title="Disconnect", control_type="Button").click_input()



if __name__ == "__main__":
    main()