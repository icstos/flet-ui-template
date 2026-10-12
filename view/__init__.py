"""视图层。

纯 Flet 声明式组件：只负责「把状态渲染成控件」与「把交互转成视图模型调用」，
不含任何业务逻辑。全部层次依赖方向为 View -> ViewModel -> Service -> Infra，
所有层均可依赖 Models。
"""

from __future__ import annotations

from view.hooks import use_view_model

__all__ = ["use_view_model"]
