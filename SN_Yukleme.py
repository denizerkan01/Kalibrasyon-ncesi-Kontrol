import os
import sys
import time
import pyperclip
import serial.tools.list_ports
from pywinauto import Desktop
from pywinauto.keyboard import send_keys
from pywinauto.application import Application

import general_functions as fnc
import Role as Role

path_arview = r"C:\Program Files\ArView\ArView.exe"
base_path = os.path.dirname(os.path.abspath(__file__)) 

def launch_arview(path):
    app = Application(backend="uia").start(path)
    dlg = app.window(auto_id="FormMain", control_type="Window")
    dlg.wait("visible ready", timeout=60)
    return dlg

def save_sn_file(file_path, sn):
    limit_file_sn = os.path.join(file_path, "Limit Dosyaları", "SN_Takip.txt")
    with open(limit_file_sn, "w", encoding="utf-8") as file:
        file.write(sn)

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


def SN_Yukleme(dlg,sn_dvc, base_path, hw_ver, pn_dvc, device_name, sn_load):

    result = {
                "sn_status": False,

    }

    if sn_dvc == "12345678":
        print("SN yüklü değil")
        result["sn_status"] = False
    else:
        print("SN yüklü")
        result["sn_status"] = True

    if result["sn_status"] == False:
        dvc = dlg.child_window(title="Device", control_type="MenuItem")
        dvc.click_input()

        send_keys("{UP}{UP}{ENTER}")
     


        fw = Desktop(backend="uia").window(title_re=".*Firmware.*")
        fw.wait("exists visible", timeout=30) 
        fw.set_focus()
        send_keys("^+h")

        #fw.print_control_identifiers(filename="tree.txt")

        ports = list(serial.tools.list_ports.comports())
            
        target_standard = fnc.find_port("Standard", ports)
        print("Standard Port:", target_standard)

        fw.child_window(title="Reload", control_type="Button").click_input()

        time.sleep(1)
        fw.child_window(title="Open", control_type="Button").click_input()
        time.sleep(1)
        #fw.print_control_identifiers(filename="tree1.txt")

        fw.child_window(title=target_standard, control_type="ListItem").click_input()
        time.sleep(3)

        fw.child_window(title="Browse",auto_id="button1", control_type="Button").click_input()


        path = os.path.join(base_path, "Limit Dosyaları")

        if pn_dvc == "M2GR051433A":
            path = os.path.join(path, "ArNavM2GR_051433_00A10901C012002F.hex")
        elif pn_dvc == "S3A097190":
            path = os.path.join(path, "ArNavS3A-097190-00A00000000S310A.hex")
            

        print(path)

        target_folder = os.path.join(base_path, path)
        
        send_keys("^l")            
        time.sleep(0.3)
        send_keys("^a{DEL}")       
        send_keys(target_folder, with_spaces=True)
        send_keys("{ENTER}")

        #fw.print_control_identifiers(filename="tree2.txt")

        fw.child_window(title="label1", auto_id="hwVersionTextBox", control_type="Edit").click_input()

        send_keys("^a")
        send_keys("{DELETE}")
        send_keys(hw_ver, with_spaces=True)

        time.sleep(3)

        fw.child_window(title="Hardware Version:", auto_id="serialNumberTextBox", control_type="Edit").click_input()

        send_keys("^a")
        send_keys("{DELETE}")
        send_keys(sn_load, with_spaces=True)

        

        fw.child_window(title="Device Serial No:", auto_id="devPartNoTextBox", control_type="Edit").click_input()

        send_keys("^a")
        send_keys("{DELETE}")
        send_keys(pn_dvc, with_spaces=True)

        fw.child_window(title="Device Part No:", auto_id="deviceNameTextBox", control_type="Edit").click_input()

        send_keys("^a")
        send_keys("{DELETE}")
        send_keys(device_name, with_spaces=True)
           
        checkbox = fw.child_window(title="Enable Hex Property Check", auto_id="cbHexPropertyCheck", control_type="CheckBox")
        print("Checkbox:", checkbox)
        state = checkbox.get_toggle_state()

        desired = "0"

        if state != desired:
            checkbox.click_input()


        fw.child_window(title="START", auto_id="startButton", control_type="Button").click_input()

        time.sleep(3)

        Role.Role()
            
        fw_update_file = os.environ.get("KALIB_FW_UPDATE_FILE")
        if not fw_update_file:
            raise RuntimeError("KALIB_FW_UPDATE_FILE is not configured; cannot wait for GUI confirmation.")

        print("@@FW_UPDATE_PENDING", flush=True)
        while not os.path.exists(fw_update_file):
            fnc.check_stop_requested()
            time.sleep(0.25)

        print("Güncellendi")
        print("@@FW_UPDATE_COMPLETED", flush=True)

        next_sn = str(int(sn_load) + 1).zfill(len(sn_load))
        save_sn_file(base_path, next_sn)
        print("Yeni SN kaydedildi:", next_sn)

        time.sleep(3)

        #fw.print_control_identifiers(filename="tree3.txt")
        fw.child_window(title="OK", auto_id="cancelButton", control_type="Button").click_input()

        time.sleep(3)
        send_keys("%{F4}")
        Role.Role()
        print("@@HARD_RESET_NOTICE", flush=True)

        time.sleep(5)

        device_folder_name = "Device"

        sn_dvc = device_sn(device_folder_name)
        print("@@SERIAL_NUMBER:" + str(sn_dvc), flush=True)

        


    return sn_dvc