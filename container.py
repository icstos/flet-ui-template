"""组合根：依赖装配。

这里是**唯一**知道「抽象接口对应哪个具体实现」的地方。所有实现按
``View -> ViewModel -> Service -> Infra`` 的顺序自底向上装配，高层拿到的是
接口而非实现，因此替换存储介质只需改动本文件。

本模块不属于五个业务层，仅承担进程启动期的连线职责。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from infra import (
    JsonSessionStore,
    Pbkdf2PasswordHasher,
    SqliteDatabase,
    SqlUserRepository,
    SqlWorkspaceRepository,
    TomlSettingsStore,
    initialize_database,
)
from service import AuthService, SettingsService, WorkspaceService
from viewmodel import (
    ChangePasswordViewModel,
    ChatDetailViewModel,
    GenericDetailViewModel,
    ListPanelViewModel,
    LoginViewModel,
    NavRailViewModel,
    RegisterViewModel,
    SearchOverlayViewModel,
    SettingsViewModel,
    ShellViewModel,
    ThemeState,
    TitleBarViewModel,
)


@dataclass(frozen=True, slots=True)
class AppContainer:
    """应用依赖容器。

    服务以 ``*_service`` 命名，视图模型以业务语义命名，避免同名歧义。
    """

    settings_service: SettingsService
    workspace_service: WorkspaceService
    auth_service: AuthService

    theme: ThemeState
    shell: ShellViewModel
    title_bar: TitleBarViewModel
    nav_rail: NavRailViewModel
    list_panel: ListPanelViewModel
    chat_detail: ChatDetailViewModel
    generic_detail: GenericDetailViewModel
    search_overlay: SearchOverlayViewModel
    login: LoginViewModel
    register: RegisterViewModel
    change_password: ChangePasswordViewModel
    settings: SettingsViewModel


def build_container(
    config_path: Path | None = None,
    session_path: Path | None = None,
) -> AppContainer:
    """自底向上装配全部依赖，并完成数据库初始化。

    Args:
        config_path: 配置文件路径；``None`` 表示使用默认位置。
        session_path: 登录状态文件路径；``None`` 表示使用默认位置。

    Returns:
        可直接供视图层使用的容器。
    """
    # ── 基础设施 ────────────────────────────────────────────
    settings_store = TomlSettingsStore(config_path)
    settings_service = SettingsService(settings_store)

    hasher = Pbkdf2PasswordHasher()
    database = SqliteDatabase(settings_service.settings().database.url)
    initialize_database(database, hasher)

    # ── 业务服务（只注入抽象接口）────────────────────────────
    workspace_service = WorkspaceService(SqlWorkspaceRepository(database))
    auth_service = AuthService(
        SqlUserRepository(database), hasher, JsonSessionStore(session_path)
    )

    # ── 视图模型 ────────────────────────────────────────────
    theme = ThemeState(settings_service)

    return AppContainer(
        settings_service=settings_service,
        workspace_service=workspace_service,
        auth_service=auth_service,
        theme=theme,
        shell=ShellViewModel(workspace_service, auth_service),
        title_bar=TitleBarViewModel(),
        nav_rail=NavRailViewModel(workspace_service, auth_service),
        list_panel=ListPanelViewModel(workspace_service, settings_service),
        chat_detail=ChatDetailViewModel(workspace_service),
        generic_detail=GenericDetailViewModel(workspace_service),
        search_overlay=SearchOverlayViewModel(workspace_service),
        login=LoginViewModel(auth_service, workspace_service),
        register=RegisterViewModel(auth_service, workspace_service),
        change_password=ChangePasswordViewModel(auth_service),
        settings=SettingsViewModel(settings_service, theme, auth_service),
    )
