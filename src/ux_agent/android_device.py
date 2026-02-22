from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


class ADBError(RuntimeError):
    """Raised when an adb command fails."""


@dataclass
class DeviceSnapshot:
    serial: str
    screenshot_path: Path
    extracted_texts: list[str]


class AndroidDeviceController:
    def __init__(self, adb_path: str = "adb", artifacts_dir: str = "artifacts") -> None:
        self.adb_path = adb_path
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def _run(self, *args: str) -> str:
        cmd = [self.adb_path, *args]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise ADBError(f"adb command failed: {' '.join(cmd)}\n{proc.stderr.strip()}")
        return proc.stdout

    def list_devices(self) -> list[str]:
        output = self._run("devices")
        devices: list[str] = []
        for line in output.strip().splitlines()[1:]:
            if not line.strip():
                continue
            serial, state = line.split(maxsplit=1)
            if state.strip() == "device":
                devices.append(serial)
        return devices

    def launch_app(self, serial: str, package_name: str) -> None:
        self._run("-s", serial, "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1")

    def dump_ui_texts(self, serial: str) -> list[str]:
        remote = "/sdcard/uidump.xml"
        self._run("-s", serial, "shell", "uiautomator", "dump", remote)
        xml_content = self._run("-s", serial, "shell", "cat", remote)
        return extract_texts_from_uixml(xml_content)

    def capture_snapshot(self, serial: str) -> DeviceSnapshot:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = self.artifacts_dir / f"{serial}_{ts}.png"
        with screenshot_path.open("wb") as fh:
            proc = subprocess.run(
                [self.adb_path, "-s", serial, "exec-out", "screencap", "-p"],
                stdout=fh,
                stderr=subprocess.PIPE,
            )
        if proc.returncode != 0:
            raise ADBError(proc.stderr.decode("utf-8", errors="ignore"))

        extracted_texts = self.dump_ui_texts(serial)
        return DeviceSnapshot(serial=serial, screenshot_path=screenshot_path, extracted_texts=extracted_texts)


def extract_texts_from_uixml(xml_content: str) -> list[str]:
    root = ET.fromstring(xml_content)
    texts: list[str] = []
    for node in root.iter("node"):
        text = node.attrib.get("text", "").strip()
        desc = node.attrib.get("content-desc", "").strip()
        if text:
            texts.append(text)
        if desc:
            texts.append(desc)
    # stable order dedupe
    return list(dict.fromkeys(texts))
