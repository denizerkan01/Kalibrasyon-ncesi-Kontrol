import serial.tools.list_ports
import general_functions as fnc

import AccTesti as AccTesti
import GyroTesti as GyroTesti
import MagnTesti as MagnTesti
import KalibIdentityTesti as KalibIdentityTesti

import Gyro_Elements as Gyro_Elements
import deneme as deneme

def UartRs232Testi(dlg, folder_path, kalibrasyon_kontrol_folder, ref_matrix_acc, firmware_version):
    
    ports = list(serial.tools.list_ports.comports())
    target_enhanced = fnc.find_port("Enhanced", ports)
    target_standard = fnc.find_port("Standard", ports)
    
    result_UART = False
        
    if fnc.try_connect(dlg, target_enhanced, "Enhanced"):
        results_uart_conn = KalibIdentityTesti.KalibIdentityTesti(dlg, folder_path, kalibrasyon_kontrol_folder, ref_matrix_acc, firmware_version)
                    
    if results_uart_conn["calib_ctrl_success"] == True:
        result_UART = True
    else:
        result_UART = False
    
    dlg.child_window(title="Disconnect", control_type="Button").click_input()
        
    if fnc.try_connect(dlg, target_standard, "Standard"):
        results_232_conn = KalibIdentityTesti.KalibIdentityTesti(dlg, folder_path, kalibrasyon_kontrol_folder, ref_matrix_acc, firmware_version)
                    
    if results_232_conn["calib_ctrl_success"] == True:
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