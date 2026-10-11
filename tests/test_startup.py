"""真实启动 CSTOS 应用，捕获运行期异常并在数秒后自动退出。

用于验证 Flet 1.0.4 下的真实启动路径（窗口创建、字体加载、组件渲染）。
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent.resolve()
PY = sys.executable
TITLE = "CSTOS"


def cleanup():
    """按命令行特征清理本项目残留进程（避免误杀用户其它 flet 程序）。"""
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


def main():
    cleanup()
    time.sleep(0.5)

    env = dict(os.environ)
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    proc = subprocess.Popen(
        [PY, str(ROOT / "main.py")],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    # 给应用 12 秒启动时间，然后读取已产生的输出
    deadline = time.time() + 12
    lines = []
    try:
        while time.time() < deadline:
            if proc.poll() is not None:
                break
            time.sleep(0.5)
    finally:
        alive = proc.poll() is None
        print(f"\n{'=' * 64}")
        print(f"进程状态: {'仍在运行(启动成功)' if alive else f'已退出 code={proc.returncode}'}")
        print("=" * 64)

        # 收尾：只杀本项目进程树
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            capture_output=True,
        )
        try:
            out, _ = proc.communicate(timeout=10)
            if out:
                lines = out.splitlines()
        except subprocess.TimeoutExpired:
            out = proc.stdout.read() if proc.stdout else ""
            lines = out.splitlines() if out else []
        cleanup()

    print("\n----- 应用输出 -----")
    for line in lines:
        print(line)
    if not lines:
        print("(无输出)")

    # 判定：出现 Traceback / AttributeError 即为失败
    joined = "\n".join(lines)
    bad_markers = [
        "Traceback (most recent call last)",
        "AttributeError",
        "TypeError",
        "ValueError",
        "RuntimeError",
        "ModuleNotFoundError",
        "Fatal error",
        "Unhandled Exception",
    ]
    found = [m for m in bad_markers if m in joined]
    if found:
        print("\n[结论] 启动过程中出现异常:")
        for m in found:
            print(f"  - {m}")
        return 1
    if alive:
        print("\n[结论] 应用成功启动并持续运行，无异常输出 ✓")
        return 0
    print("\n[结论] 应用已退出，请检查上方输出")
    return 1


if __name__ == "__main__":
    sys.exit(main())
