"""视图模型基础设施。

约定：

* 视图模型是**纯 Python 类**，持有 UI 状态并调用业务服务；
* 状态变更后调用 :meth:`Observable.notify`，视图层据此重新派生界面；
* 需要「跳转到某路由」的方法**返回路由字符串**，由视图层执行实际导航——
  视图模型不接触任何 UI 组件，也不操作页面。
"""

from __future__ import annotations

from models.reactive import Observable

type RouteTarget = str | None
"""视图模型返回给视图的导航目标；``None`` 表示无需跳转。"""


class ViewModel(Observable):
    """视图模型基类。

    继承 :class:`~models.reactive.Observable`，无额外行为。
    """
