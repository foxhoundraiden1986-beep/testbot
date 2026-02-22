from __future__ import annotations

import html
import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from ux_agent.android_device import ADBError, AndroidDeviceController

controller = AndroidDeviceController()


def _page(devices: list[str] | None = None, snapshot: dict | None = None, error: str | None = None) -> str:
    devices_block = f"<pre>{html.escape(json.dumps(devices, ensure_ascii=False, indent=2))}</pre>" if devices is not None else ""
    snapshot_block = ""
    if snapshot:
        texts = html.escape(json.dumps(snapshot["texts"], ensure_ascii=False, indent=2))
        snapshot_block = (
            f"<p>截图文件：<a href='/artifact/{html.escape(snapshot['name'])}'>{html.escape(snapshot['name'])}</a></p>"
            f"<p>识别文本（UI树）：</p><pre>{texts}</pre>"
        )
    error_block = f"<div><strong>错误：</strong><pre>{html.escape(error)}</pre></div>" if error else ""
    return f"""<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'/><title>Android UX Agent 控制台</title>
<style>body{{font-family:sans-serif;max-width:980px;margin:20px auto;line-height:1.6}} .card{{border:1px solid #ddd;border-radius:8px;padding:16px;margin-bottom:12px}} input,button{{padding:8px;margin:4px 0}}</style>
</head><body>
<h1>Android UX Agent 控制台（MVP）</h1>
<div class='card'><h3>1) 查询已连接设备</h3><form method='post' action='/devices'><button type='submit'>刷新设备列表</button></form>{devices_block}</div>
<div class='card'><h3>2) 打开 APP</h3><form method='post' action='/launch'>
<div>设备序列号：<input name='serial' required placeholder='如 emulator-5554'/></div>
<div>包名：<input name='package_name' required placeholder='如 com.android.settings' style='width:360px'/></div>
<button type='submit'>打开 APP</button></form></div>
<div class='card'><h3>3) 截图 + 文本识别（基于 UI 树）</h3><form method='post' action='/snapshot'>
<div>设备序列号：<input name='serial' required placeholder='如 emulator-5554'/></div>
<button type='submit'>执行截图与识别</button></form>{snapshot_block}</div>
{error_block}
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send_html(self, body: str, code: int = 200) -> None:
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload: dict, code: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _post_form(self) -> dict[str, str]:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        parsed = parse_qs(raw)
        return {k: v[0] for k, v in parsed.items()}

    def do_GET(self) -> None:
        if self.path == "/":
            self._send_html(_page())
            return
        if self.path.startswith("/artifact/"):
            name = self.path.removeprefix("/artifact/")
            path = Path("artifacts") / name
            if not path.exists():
                self._send_json({"ok": False, "error": "not found"}, code=404)
                return
            data = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self._send_json({"ok": False, "error": "not found"}, code=404)

    def do_POST(self) -> None:
        if self.path == "/devices":
            try:
                self._send_html(_page(devices=controller.list_devices()))
            except ADBError as err:
                self._send_html(_page(error=str(err)), code=400)
            return

        form = self._post_form()
        if self.path == "/launch":
            serial = form.get("serial", "").strip()
            package_name = form.get("package_name", "").strip()
            if not serial or not package_name:
                self._send_json({"ok": False, "error": "serial/package_name required"}, code=400)
                return
            try:
                controller.launch_app(serial, package_name)
                self._send_json({"ok": True, "serial": serial, "package_name": package_name})
            except ADBError as err:
                self._send_json({"ok": False, "error": str(err)}, code=400)
            return

        if self.path == "/snapshot":
            serial = form.get("serial", "").strip()
            if not serial:
                self._send_html(_page(error="serial required"), code=400)
                return
            try:
                snap = controller.capture_snapshot(serial)
                self._send_html(_page(snapshot={"name": snap.screenshot_path.name, "texts": snap.extracted_texts}))
            except ADBError as err:
                self._send_html(_page(error=str(err)), code=400)
            return

        self._send_json({"ok": False, "error": "not found"}, code=404)


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Web console running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
