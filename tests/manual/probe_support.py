"""真机验证脚本的公共支撑。

集中处理四件事，避免在各脚本中重复：
    * 项目路径与探针工作目录；
    * 按命令行特征清理本项目残留进程（不误伤用户其它程序）；
    * DPI 感知的窗口逻辑尺寸换算；
    * 以 UTF-8、无缓冲方式启动应用并回收输出。

坐标说明：``windows_input_driver.click_at`` 接收的是**逻辑**客户区坐标，
即物理像素除以 ``GetDpiForWindow/96``。用物理坐标点击会越界被静默跳过。
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PROBE = ROOT / ".workbuddy" / "probe"
PY = sys.executable
WINDOW_TITLE = "CSTOS"

PROBE.mkdir(parents=True, exist_ok=True)

_SKILL_SCRIPTS = Path.home() / ".workbuddy" / "skills" / "flet-desktop-ui-probe" / "scripts"
if str(_SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SKILL_SCRIPTS))

import windows_input_driver as drv

drv.ROOT = PROBE
drv.LOG = PROBE / "_probe.log"
drv.DRIVE_LOG = PROBE / "_probe_drive.log"

# 匹配本项目进程的命令行特征，避免误杀用户其它 flet / python 程序
_PS_CLEANUP = (
    "Get-CimInstance Win32_Process "
    "-Filter \"Name='flet.exe' or Name='python.exe'\" "
    "| Where-Object { $_.CommandLine -like '*cs-ui-template*' } "
    "| ForEach-Object { Stop-Process -Id $_.ProcessId -Force "
    "-ErrorAction SilentlyContinue }"
)


def cleanup_processes() -> None:
    """清理本项目残留的 flet / python 进程。"""
    subprocess.run(
        ["powershell", "-NoProfile", "-Command", _PS_CLEANUP],
        capture_output=True,
        check=False,
    )


def logical_size(hwnd: int) -> tuple[int, int, float]:
    """返回窗口的逻辑宽高与 DPI 缩放比。"""
    rect = drv.rect_of(hwnd)
    dpi = ctypes.windll.user32.GetDpiForWindow(hwnd) / 96.0
    return (
        int((rect.right - rect.left) / dpi),
        int((rect.bottom - rect.top) / dpi),
        dpi,
    )


def launch() -> subprocess.Popen[str]:
    """以 UTF-8、无缓冲方式启动应用。"""
    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.Popen(
        [PY, str(ROOT / "main.py")],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def teardown(proc: subprocess.Popen[str]) -> str:
    """结束应用进程并返回其完整输出。"""
    drv.kill_tree(proc.pid)
    try:
        out, _ = proc.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        out = ""
    cleanup_processes()
    return out or ""


def report_errors(output: str) -> int:
    """打印输出中的异常片段；有异常返回 1，否则 0。"""
    lines = output.splitlines()
    bad = [line for line in lines if "Traceback" in line or "Error" in line]
    if not bad:
        return 0
    print("----- 应用侧异常 -----")
    print("\n".join(lines[-25:]))
    return 1
