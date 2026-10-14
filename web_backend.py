from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PAGE = ROOT / "web_gui.html"
STOP_FILE = ROOT / ".kalib_stop_requested"
FW_UPDATE_FILE = ROOT / ".kalib_fw_update_completed"
HOST = "127.0.0.1"
PORT = 8765

lock = threading.RLock()
process: subprocess.Popen[str] | None = None
log_lines: deque[str] = deque(maxlen=300)
started_at: float | None = None
part_number: str | None = None
serial_number: str | None = None
fw_update_pending = False


def read_saved_part_number() -> str | None:
    config = ROOT / "Device" / "config.txt"
    try:
        with config.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                key, separator, value = line.partition("=")
                if separator and key.strip() == "DevicePN":
                    return value.strip().strip('"').strip("'") or None
    except OSError:
        pass
    return None

def state() -> dict:
    with lock:
        running = process is not None and process.poll() is None
        if running and STOP_FILE.exists():
            status = "stopping"
        elif running:
            status = "running"
        elif process is None:
            status = "idle"
        elif STOP_FILE.exists() and process.returncode == 0:
            status = "stopped"
        elif process.returncode == 0:
            status = "completed"
        else:
            status = "failed"
        try:
            from serial.tools import list_ports
            ports = list(list_ports.comports())
            standard = next((p.device for p in ports if "Standard" in p.description), None)
        except Exception:
            standard = None
        return {
            "status": status,
            "running": running,
            "device_port": standard,
            "returncode": process.returncode if process and not running else None,
            "started_at": started_at,
            "part_number": part_number,
            "serial_number": serial_number,
            "fw_update_pending": fw_update_pending and running,
            "logs": list(log_lines),
        }


def read_output(child: subprocess.Popen[str]) -> None:
    global part_number, serial_number, fw_update_pending
    assert child.stdout is not None
    for line in child.stdout:
        clean = line.rstrip()
        with lock:
            log_lines.append(clean)
            if clean.startswith("@@PART_NUMBER:"):
                part_number = clean.split(":", 1)[1].strip()
            elif clean.startswith("@@SERIAL_NUMBER:"):
                serial_number = clean.split(":", 1)[1].strip()
            elif clean == "@@FW_UPDATE_PENDING":
                fw_update_pending = True
            elif clean == "@@FW_UPDATE_COMPLETED":
                fw_update_pending = False

def start_tests() -> tuple[int, dict]:
    global process, started_at, part_number, serial_number, fw_update_pending
    with lock:
        if process is not None and process.poll() is None:
            return 409, state()
        try:
            STOP_FILE.unlink(missing_ok=True)
            FW_UPDATE_FILE.unlink(missing_ok=True)
            log_lines.clear()
            part_number = None
            serial_number = None
            fw_update_pending = False
            env = os.environ.copy()
            env["KALIB_STOP_FILE"] = str(STOP_FILE)
            env["KALIB_FW_UPDATE_FILE"] = str(FW_UPDATE_FILE)
            process = subprocess.Popen(
                [sys.executable, "-u", str(ROOT / "main.py")],
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
            started_at = time.time()
            threading.Thread(target=read_output, args=(process,), daemon=True).start()
            log_lines.append("Web GUI started the Python test workflow.")
            return 202, state()
        except Exception as exc:
            log_lines.append(f"Could not start Python: {exc}")
            return 500, state()


def confirm_fw_update() -> tuple[int, dict]:
    global fw_update_pending
    with lock:
        if process is None or process.poll() is not None or not fw_update_pending:
            return 409, {"error": "Firmware update confirmation is not currently requested.", **state()}
        FW_UPDATE_FILE.touch()
        fw_update_pending = False
        log_lines.append("Firmware update confirmation received from the GUI.")
        return 202, state()


def request_stop() -> tuple[int, dict]:
    with lock:
        if process is None or process.poll() is not None:
            return 409, state()
        STOP_FILE.touch()
        log_lines.append("Safe stop requested; the current measurement will finish first.")
        return 202, state()


class Handler(BaseHTTPRequestHandler):
    server_version = "KalibLocal/1.0"

    def _send(self, code: int, content_type: str, body: bytes) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, value: dict) -> None:
        self._send(code, "application/json; charset=utf-8", json.dumps(value).encode("utf-8"))

    def _is_local(self) -> bool:
        if self.headers.get("Host") != f"{HOST}:{PORT}":
            return False
        origin = self.headers.get("Origin")
        return origin in (None, f"http://{HOST}:{PORT}")

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if not self._is_local():
            self._json(403, {"error": "Local access only."})
        elif path in ("/", "/index.html"):
            try:
                page = PAGE.read_bytes()
            except OSError as exc:
                self._send(500, "text/plain; charset=utf-8", str(exc).encode())
            else:
                self._send(200, "text/html; charset=utf-8", page)
        elif path == "/api/status":
            self._json(200, state())
        else:
            self._json(404, {"error": "Not found."})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if not self._is_local():
            self._json(403, {"error": "Local access only."})
        elif path == "/api/start":
            code, result = start_tests()
            self._json(code, result)
        elif path == "/api/stop":
            code, result = request_stop()
            self._json(code, result)
        elif path == "/api/fw-update-complete":
            code, result = confirm_fw_update()
            self._json(code, result)
        else:
            self._json(404, {"error": "Not found."})

    def log_message(self, fmt: str, *args: object) -> None:
        if sys.stdout is not None:
            print(f"[web] {self.address_string()} - {fmt % args}")


def main() -> None:
    if not PAGE.is_file():
        raise SystemExit(f"GUI page not found: {PAGE}")
    if sys.stdout is not None:
        print(f"Kalib GUI available at http://{HOST}:{PORT}/")
        print("This service is local to this PC. Keep the device connected before starting tests.")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()



