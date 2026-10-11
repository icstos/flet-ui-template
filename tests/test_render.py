"""启动 CSTOS 并用 PrintWindow 抓取真实窗口截图，检测 Flutter 侧灰块。

依据技能文档：Python 侧无异常不代表 Flutter 渲染成功 ——
不可渲染的控件会被 Flutter 的 ErrorWidget 顶替，表现为大片灰色 (#BDBDBD)。
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
PROBE = ROOT / ".workbuddy" / "probe"
PY = sys.executable

sys.path.insert(0, str(Path.home() / ".workbuddy/skills/flet-desktop-ui-probe/scripts"))
import windows_input_driver as drv  # noqa: E402

drv.ROOT = PROBE
drv.LOG = PROBE / "_probe_ui.log"
drv.DRIVE_LOG = PROBE / "_probe_drive.log"

PROBE.mkdir(parents=True, exist_ok=True)


def cleanup():
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Get-CimInstance Win32_Process -Filter \"Name='flet.exe' or Name='python.exe'\" "
            "| Where-Object { $_.CommandLine -like '*cs-ui-template*' } "
            "| ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }",
        ],
        capture_output=True,
    )


def grey_ratio(png):
    """统计内容区灰色像素占比，判断 Flutter 侧是否渲染成 ErrorWidget。"""
    from PIL import Image

    img = Image.open(png).convert("RGB")
    w, h = img.size
    box = img.crop((int(w * 0.08), int(h * 0.18), int(w * 0.92), int(h * 0.92)))
    px = list(box.getdata())
    greyish = sum(
        1 for r, g, b in px if abs(r - g) <= 6 and abs(g - b) <= 6 and 0xAC <= r <= 0xCC
    )
    return greyish / len(px)


def main():
    cleanup()
    time.sleep(0.5)

    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"
    proc = subprocess.Popen(
        [PY, str(ROOT / "main.py")],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
    )

    try:
        # 等窗口出现
        hwnd = None
        end = time.time() + 45
        while time.time() < end:
            hwnd = drv.find_window_pid("CSTOS", proc.pid)
            if hwnd:
                break
            time.sleep(0.5)

        if not hwnd:
            print("! 未找到 CSTOS 窗口")
            return 1

        print(f"找到窗口 hwnd={hwnd}")
        time.sleep(4.0)  # 等内容渲染稳定

        # 抓两次，丢掉可能滞后的第一帧
        out1 = PROBE / "_shot_1.png"
        out2 = PROBE / "_shot_2.png"
        drv.screenshot(hwnd, out1)
        time.sleep(0.6)
        drv.screenshot(hwnd, out2)

        ratio = grey_ratio(out2)
        print(f"内容区灰色占比: {ratio:.4f}  (阈值 0.55)")
        print(f"截图: {out2}")

        if ratio > 0.55:
            print("[结论] 存在大片灰块 —— Flutter 侧渲染失败 (ErrorWidget)")
            return 1
        print("[结论] 无灰块，Flutter 侧渲染正常 ✓")
        return 0
    finally:
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
        try:
            out, _ = proc.communicate(timeout=8)
            if out:
                tail = out.decode("utf-8", "replace")[-1500:]
                if "Traceback" in tail or "Error" in tail:
                    print("\n----- 应用侧异常输出 -----")
                    print(tail)
        except Exception:
            pass
        cleanup()


if __name__ == "__main__":
    sys.exit(main())
