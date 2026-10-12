"""响应式状态原语。

纯 Python 实现，不依赖任何 UI 框架。这是 ViewModel 驱动声明式界面更新的
唯一机制：状态变更 -> :meth:`Observable.notify` -> 订阅者（视图层桥接）被唤醒
-> 视图依据新状态重新派生。

设计约束：
    * 只承载「状态 + 通知」，不含任何业务规则；
    * 同步通知，保证一次状态变更内视图看到一致快照；
    * 订阅返回一个取消函数，便于视图卸载时精确退订。
"""

from __future__ import annotations

from collections.abc import Callable

type Listener = Callable[[], None]
"""状态变更监听器。"""


class Observable:
    """可被订阅的状态持有者。

    子类通过公开属性持有状态，在**任何**状态发生变更后调用
    :meth:`notify` 即可；无需逐字段声明，也无需引入响应式魔法。

    Example:
        ```python
        class Counter(Observable):
            def __init__(self) -> None:
                super().__init__()
                self.value = 0

            def increment(self) -> None:
                self.value += 1
                self.notify()
        ```
    """

    __slots__ = ("_listeners",)

    def __init__(self) -> None:
        self._listeners: set[Listener] = set()

    def subscribe(self, listener: Listener) -> Callable[[], None]:
        """注册监听器。

        Args:
            listener: 状态变更时被调用的无参函数。

        Returns:
            取消订阅的函数；重复调用安全。
        """
        self._listeners.add(listener)

        def unsubscribe() -> None:
            self._listeners.discard(listener)

        return unsubscribe

    def notify(self) -> None:
        """通知所有监听器状态已变更。

        遍历前对监听器集合取快照，因此监听器在回调中退订或新增都不会
        破坏本次遍历。
        """
        for listener in tuple(self._listeners):
            listener()

    @property
    def listener_count(self) -> int:
        """当前监听器数量，便于测试断言订阅是否泄漏。"""
        return len(self._listeners)
