import os
import time
import pyperclip
from pywinauto.keyboard import send_keys

def _parse_and_compare(lines, key_name, ref_matrix):

    for raw_line in lines:
        line = raw_line.strip()

        if line.startswith(key_name):

            parts = line.split("=")
            if len(parts) < 2:
                return False

            rhs = parts[1].strip()

            rhs = rhs.replace("[", "").replace("]", "")

            try:
                parsed_vec = [float(tok.strip()) for tok in rhs.split(",") if tok.strip()]
            except ValueError:
                parsed_vec = []

            if not parsed_vec:
                return False

            return parsed_vec == [float(v) for v in ref_matrix]

    return False

def _parse_and_compare_str(lines, key_name, expected_value):

    for raw_line in lines:
        line = raw_line.strip()

        if line.startswith(key_name):

            parts = line.split("=")
            if len(parts) < 2:
                return False

            rhs = parts[1].strip()

            rhs = rhs.replace('"', "").strip()

            return rhs == expected_value

    return False

def KalibIdentityTesti(dlg, base_path, kalibrasyon_kontrol_folder, ref_matrix, firmware_version):

    time.sleep(5)
    dlg.child_window(title="Settings", control_type="Button").click_input()
    time.sleep(5)
    send_keys("^+h")
    dlg.child_window(title="Copy to Clipboard", control_type="Pane").click_input()
    time.sleep(5)
    send_keys("%{F4}")

    target_folder = os.path.join(base_path, kalibrasyon_kontrol_folder)

    config_path = os.path.join(target_folder, "config.txt")
    clipboard_content = pyperclip.paste()

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(clipboard_content)

    try:
        with open(config_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as e:
        raise IOError(f"check_calibration_factors: Cannot open file: {config_path}") from e

    firmware_version_match = _parse_and_compare_str(lines, "FirmwareVersion", firmware_version)


    acc_is_calibrated = _parse_and_compare(lines, "MiscCalibAccFac", ref_matrix)
    gyro_is_calibrated = _parse_and_compare(lines, "MiscCalibGyroFac", ref_matrix)
    magn_is_calibrated = _parse_and_compare(lines, "MiscCalibMagFac", ref_matrix)

    calib_ctrl_success = (
        acc_is_calibrated
        and gyro_is_calibrated
        and magn_is_calibrated
    )


    return {
        "acc_is_calibrated": acc_is_calibrated,
        "gyro_is_calibrated": gyro_is_calibrated,
        "magn_is_calibrated": magn_is_calibrated,
        "calib_ctrl_success": calib_ctrl_success,
        "firmware_version_match": firmware_version_match
    }