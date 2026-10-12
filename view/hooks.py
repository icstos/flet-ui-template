"""视图层与视图模型之间的桥接 hooks。

这是全应用**唯一**把「外部状态对象」接入 Flet 渲染管线的地方：
订阅视图模型 -> 状态变更时自增一个本地计数 -> 触发当前组件重新渲染。
组件因此永远只是「当前状态的纯函数」。
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from models.reactive import Observable


def use_view_model[T: Observable](view_model: T) -> T:
    """订阅视图模型并返回它。

    视图模型状态变化时，当前组件会重新渲染。

    Args:
        view_model: 要订阅的视图模型（或任何 :class:`~models.reactive.Observable`）。

    Returns:
        传入的视图模型本身，便于链式书写。
    """
    _, bump = ft.use_state(0)

    def setup() -> Callable[[], None]:
        def on_change() -> None:
            bump(lambda count: count + 1)

        return view_model.subscribe(on_change)

    ft.use_effect(setup, dependencies=[view_model])
    return view_model
