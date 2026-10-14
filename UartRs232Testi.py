import serial.tools.list_ports
import general_functions as fnc
import KalibIdentityTesti as KalibIdentityTesti


def UartRs232Testi(dlg, folder_path, kalibrasyon_kontrol_folder, ref_matrix_acc, firmware_version):

    result = {
                "Conn_Uart": False,
                "Conn_232": False,
                "Conn_Result": False,

    }
    ports = list(serial.tools.list_ports.comports())
    target_enhanced = fnc.find_port("Enhanced", ports)
    target_standard = fnc.find_port("Standard", ports)

    result_uart = False
    result_232 = False
    connected = False

    if target_enhanced:
        try:
            connected = fnc.try_connect(dlg, target_enhanced, "Enhanced")
        except Exception:
            connected = False
        if connected:
            results_uart_conn = KalibIdentityTesti.KalibIdentityTesti(
                dlg, folder_path, kalibrasyon_kontrol_folder, ref_matrix_acc, firmware_version
            )
            result_uart = results_uart_conn.get("calib_ctrl_success") == True
            result["Conn_Uart"] = result_uart
            dlg.child_window(title="Disconnect", control_type="Button").click_input()
            connected = False

    if target_standard:
        try:
            connected = fnc.try_connect(dlg, target_standard, "Standard")
        except Exception:
            connected = False
        if connected:
            results_232_conn = KalibIdentityTesti.KalibIdentityTesti(
                dlg, folder_path, kalibrasyon_kontrol_folder, ref_matrix_acc, firmware_version
            )
            result_232 = results_232_conn.get("calib_ctrl_success") == True
            result["Conn_232"] = result_232
            dlg.child_window(title="Disconnect", control_type="Button").click_input()
            connected = False

    result_conn = result_uart and result_232

    result["Conn_Result"] = result_conn
    if result["Conn_Result"]:
        print("Test 6: BAŞARILI")
    else:
        if not result["Conn_Uart"]:
            print("UART ile Bağlanılamadı")
        if not result["Conn_232"]:
            print("RS232 ile Bağlanılamadı")

    return result
