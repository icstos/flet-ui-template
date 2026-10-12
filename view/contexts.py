"""视图层的依赖注入上下文。

整棵组件树共享**一个**容器上下文；组件通过 :func:`use_container` 取到容器，
再用 :func:`~view.hooks.use_view_model` 订阅自己关心的视图模型。
这样视图无需层层透传参数，也不会退化成全局单例。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, cast

import flet as ft

if TYPE_CHECKING:
    from container import AppContainer

_ContainerContext = ft.create_context(cast("AppContainer | None", None))


def use_container() -> AppContainer:
    """获取当前组件树共享的应用容器。

    Returns:
        组合根装配出的 :class:`~container.AppContainer`。

    Raises:
        RuntimeError: 组件树未被 :func:`provide_container` 包裹时抛出。
    """
    container = ft.use_context(_ContainerContext)
    if container is None:
        raise RuntimeError(
            "应用容器未注入：请确保根组件使用 provide_container() 包裹。"
        )
    return container


def provide_container[T](container: AppContainer, build: Callable[[], T]) -> T:
    """把容器注入子树。

    Args:
        container: 待注入的应用容器。
        build: 在容器作用域内构建子树的回调。

    Returns:
        ``build`` 的返回值。
    """
    return _ContainerContext(container, build)
