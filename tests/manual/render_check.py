"""启动 CSTOS 并抓取真实窗口截图，检测 Flutter 侧灰块。

依据 Flet 桌面探针的经验：Python 侧无异常**不代表** Flutter 渲染成功 ——
不可渲染的控件会被 Flutter 的 ErrorWidget 顶替，表现为大片灰色 (#BDBDBD)。
"""

from __future__ import annotations

import sys
import time

from PIL import Image
from probe_support import (
    WINDOW_TITLE,
    cleanup_processes,
    drv,
    launch,
    report_errors,
    teardown,
)

GREY_RATIO_THRESHOLD = 0.55
"""内容区灰色像素占比超过该值即判定为渲染失败。"""


def grey_ratio(png) -> float:
    """统计内容区灰色像素占比，用于识别 Flutter ErrorWidget。"""
    image = Image.open(png).convert("RGB")
    width, height = image.size
    box = image.crop(
        (int(width * 0.08), int(height * 0.18), int(width * 0.92), int(height * 0.92))
    )
    pixels = list(box.get_flattened_data())
    greyish = sum(
        1
        for red, green, blue in pixels
        if abs(red - green) <= 6 and abs(green - blue) <= 6 and 0xAC <= red <= 0xCC
    )
    return greyish / len(pixels)


def main() -> int:
    cleanup_processes()
    time.sleep(0.5)

    ratio = 1.0
    proc = launch()
    try:
        hwnd = drv.find_window_pid(WINDOW_TITLE, proc.pid, timeout=45)
        if not hwnd:
            print(f"! 未找到 {WINDOW_TITLE} 窗口")
            return 1

        print(f"找到窗口 hwnd={hwnd}")
        time.sleep(4.0)  # 等内容渲染稳定

        # 抓两次并丢弃可能滞后的第一帧
        first = drv.ROOT / "_shot_1.png"
        final = drv.ROOT / "_shot_2.png"
        drv.screenshot(hwnd, first)
        time.sleep(0.6)
        drv.screenshot(hwnd, final)

        ratio = grey_ratio(final)
        print(f"内容区灰色占比: {ratio:.4f}  (阈值 {GREY_RATIO_THRESHOLD})")
        print(f"截图: {final}")
    finally:
        output = teardown(proc)

    if report_errors(output):
        return 1

    if ratio > GREY_RATIO_THRESHOLD:
        print("[结论] 存在大片灰块 —— Flutter 侧渲染失败 (ErrorWidget)")
        return 1
    print("[结论] 无灰块，Flutter 侧渲染正常 ✓")
    return 0


if __name__ == "__main__":
    sys.exit(main())
