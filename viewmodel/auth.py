"""认证相关视图模型：登录、注册、修改密码。

表单校验（非空、两次输入一致）属于交互约束，放在视图模型；
凭据是否正确、用户名是否被占用等业务判定则由 :class:`AuthService` 负责。
"""

from __future__ import annotations

from models import ModuleId
from service import AuthService, WorkspaceService
from viewmodel.base import RouteTarget, ViewModel

# 用户可见的提示文案
ERROR_EMPTY_CREDENTIALS = "用户名和密码不能为空"
ERROR_PASSWORD_MISMATCH = "两次输入的密码不一致"
ERROR_PASSWORD_MISMATCH_NEW = "两次输入的新密码不一致"
ERROR_EMPTY_PASSWORD = "密码不能为空"
ERROR_BAD_CREDENTIALS = "用户名或密码错误"
ERROR_USERNAME_TAKEN = "用户名已存在"
ERROR_NOT_LOGGED_IN = "请先登录"
ERROR_OLD_PASSWORD = "旧密码错误"
SUCCESS_PASSWORD_CHANGED = "密码修改成功"


class _CredentialForm(ViewModel):
    """带错误提示的表单基类。"""

    def __init__(self) -> None:
        super().__init__()
        self._error: str = ""

    @property
    def error(self) -> str:
        """当前错误提示；无错误时为空串。"""
        return self._error

    def _set_error(self, message: str) -> None:
        self._error = message
        self.notify()


class LoginViewModel(_CredentialForm):
    """登录表单。

    Args:
        auth: 认证业务服务。
        workspace: 工作区业务服务（用于计算登录后的默认页）。
    """

    def __init__(self, auth: AuthService, workspace: WorkspaceService) -> None:
        super().__init__()
        self._auth = auth
        self._workspace = workspace
        self._username: str = ""
        self._password: str = ""

    @property
    def username(self) -> str:
        """用户名输入值。"""
        return self._username

    @property
    def password(self) -> str:
        """密码输入值。"""
        return self._password

    def set_username(self, value: str) -> None:
        """更新用户名。"""
        self._username = value
        self.notify()

    def set_password(self, value: str) -> None:
        """更新密码。"""
        self._password = value
        self.notify()

    def submit(self) -> RouteTarget:
        """校验并登录。

        Returns:
            登录成功返回默认会话路由，失败返回 ``None``。
        """
        session = self._auth.login(self._username or "", self._password or "")
        if session is None:
            self._set_error(ERROR_BAD_CREDENTIALS)
            return None
        self._set_error("")
        return self._default_route()

    def _default_route(self) -> str:
        """登录成功后的落地页。"""
        return f"/{ModuleId.CHAT}/{self._workspace.default_item_id(ModuleId.CHAT)}"


class RegisterViewModel(_CredentialForm):
    """注册表单。

    Args:
        auth: 认证业务服务。
        workspace: 工作区业务服务。
    """

    def __init__(self, auth: AuthService, workspace: WorkspaceService) -> None:
        super().__init__()
        self._auth = auth
        self._workspace = workspace
        self._username: str = ""
        self._password: str = ""
        self._confirm: str = ""

    @property
    def username(self) -> str:
        """用户名输入值。"""
        return self._username

    @property
    def password(self) -> str:
        """密码输入值。"""
        return self._password

    @property
    def confirm(self) -> str:
        """确认密码输入值。"""
        return self._confirm

    def set_username(self, value: str) -> None:
        """更新用户名。"""
        self._username = value
        self.notify()

    def set_password(self, value: str) -> None:
        """更新密码。"""
        self._password = value
        self.notify()

    def set_confirm(self, value: str) -> None:
        """更新确认密码。"""
        self._confirm = value
        self.notify()

    def submit(self) -> RouteTarget:
        """校验并注册（成功后自动登录）。

        Returns:
            注册成功返回默认会话路由，失败返回 ``None``。
        """
        username = (self._username or "").strip()
        password = self._password or ""
        confirm = self._confirm or ""

        if not username or not password:
            self._set_error(ERROR_EMPTY_CREDENTIALS)
            return None
        if password != confirm:
            self._set_error(ERROR_PASSWORD_MISMATCH)
            return None

        session = self._auth.register(username, password)
        if session is None:
            self._set_error(ERROR_USERNAME_TAKEN)
            return None

        self._set_error("")
        return f"/{ModuleId.CHAT}/{self._workspace.default_item_id(ModuleId.CHAT)}"


class ChangePasswordViewModel(_CredentialForm):
    """修改密码表单。

    Args:
        auth: 认证业务服务。
    """

    def __init__(self, auth: AuthService) -> None:
        super().__init__()
        self._auth = auth
        self._old_password: str = ""
        self._new_password: str = ""
        self._confirm: str = ""
        self._message: str = ""

    @property
    def old_password(self) -> str:
        """旧密码输入值。"""
        return self._old_password

    @property
    def new_password(self) -> str:
        """新密码输入值。"""
        return self._new_password

    @property
    def confirm(self) -> str:
        """确认新密码输入值。"""
        return self._confirm

    @property
    def message(self) -> str:
        """成功提示；无提示时为空串。"""
        return self._message

    def set_old_password(self, value: str) -> None:
        """更新旧密码。"""
        self._old_password = value
        self.notify()

    def set_new_password(self, value: str) -> None:
        """更新新密码。"""
        self._new_password = value
        self.notify()

    def set_confirm(self, value: str) -> None:
        """更新确认新密码。"""
        self._confirm = value
        self.notify()

    def submit(self) -> None:
        """校验并提交改密请求。"""
        old = self._old_password or ""
        new = self._new_password or ""
        confirm = self._confirm or ""

        if not old or not new:
            self._fail(ERROR_EMPTY_PASSWORD)
            return
        if new != confirm:
            self._fail(ERROR_PASSWORD_MISMATCH_NEW)
            return
        if self._auth.current_session() is None:
            self._fail(ERROR_NOT_LOGGED_IN)
            return

        if self._auth.change_password(old, new):
            self._error = ""
            self._message = SUCCESS_PASSWORD_CHANGED
            self._old_password = ""
            self._new_password = ""
            self._confirm = ""
            self.notify()
            return

        self._fail(ERROR_OLD_PASSWORD)

    def _fail(self, message: str) -> None:
        """设置错误提示并清除成功提示。"""
        self._error = message
        self._message = ""
        self.notify()
