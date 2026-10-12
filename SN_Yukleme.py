import os
import time
import serial.tools.list_ports
from pywinauto import Desktop
from pywinauto.keyboard import send_keys
from pywinauto.application import Application

import general_functions as fnc

path_arview = r"C:\Program Files\ArView\ArView.exe"
base_path = os.path.dirname(os.path.abspath(__file__)) 

def launch_arview(path):
    app = Application(backend="uia").start(path)
    dlg = app.window(auto_id="FormMain", control_type="Window")
    dlg.wait("visible ready", timeout=60)
    return dlg


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
        path = os.path.join(path, "ArNavM2GR_051433_00A10901C012002F.hex")

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
            
        


    return sn_dvc