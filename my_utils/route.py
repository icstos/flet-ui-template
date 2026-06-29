"""路由工具模块。

提供路由路径的解析功能。
"""


def parse_workspace(location: str) -> tuple[str, str]:
    """解析工作区路由路径。

    将形如 "/chat/zhang" 的路径解析为模块 ID 和条目 ID。

    Args:
        location: 路由路径字符串。

    Returns:
        包含 (module_id, item_id) 的元组。
        路径无效时 module_id 默认为 "chat"，item_id 默认为空串。
    """
    parts = location.strip("/").split("/")
    module_id = parts[0] if parts else "chat"
    item_id = parts[1] if len(parts) > 1 else ""
    return module_id, item_id
