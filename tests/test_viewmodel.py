"""视图模型与业务行为的单元测试。

全部为纯 Python 断言，不启动 UI —— 这正是分层带来的可测性：
状态与业务逻辑可以脱离 Flet 独立验证。
"""

from __future__ import annotations

import pytest

from infra.seed import DEFAULT_PASSWORD, DEFAULT_USERNAME
from viewmodel import (
    ChatDetailViewModel,
    ListPanelViewModel,
    LoginViewModel,
    RegisterViewModel,
    SearchOverlayViewModel,
    ShellViewModel,
    ThemeState,
)

# ── 认证 ────────────────────────────────────────────────────


class TestAuth:
    def test_login_success_returns_default_route(self, container) -> None:
        vm = LoginViewModel(container.auth_service, container.workspace_service)
        vm.set_username(DEFAULT_USERNAME)
        vm.set_password(DEFAULT_PASSWORD)

        route = vm.submit()

        assert route is not None and route.startswith("/chat/")
        assert vm.error == ""

    def test_login_failure_sets_error(self, container) -> None:
        vm = LoginViewModel(container.auth_service, container.workspace_service)
        vm.set_username(DEFAULT_USERNAME)
        vm.set_password("wrong-password")

        assert vm.submit() is None
        assert vm.error == "用户名或密码错误"

    def test_register_rejects_empty_then_mismatch(self, container) -> None:
        vm = RegisterViewModel(container.auth_service, container.workspace_service)

        assert vm.submit() is None
        assert vm.error == "用户名和密码不能为空"

        vm.set_username("newbie")
        vm.set_password("secret")
        vm.set_confirm("different")
        assert vm.submit() is None
        assert vm.error == "两次输入的密码不一致"

    def test_register_then_duplicate(self, container) -> None:
        vm = RegisterViewModel(container.auth_service, container.workspace_service)
        vm.set_username("newbie")
        vm.set_password("secret")
        vm.set_confirm("secret")

        assert vm.submit() is not None

        dup = RegisterViewModel(container.auth_service, container.workspace_service)
        dup.set_username("newbie")
        dup.set_password("secret")
        dup.set_confirm("secret")
        assert dup.submit() is None
        assert dup.error == "用户名已存在"

    def test_change_password_flow(self, container) -> None:
        login = LoginViewModel(container.auth_service, container.workspace_service)
        login.set_username(DEFAULT_USERNAME)
        login.set_password(DEFAULT_PASSWORD)
        login.submit()

        vm = container.change_password
        vm.set_old_password("wrong")
        vm.set_new_password("brand-new")
        vm.set_confirm("brand-new")
        vm.submit()
        assert vm.error == "旧密码错误"

        vm.set_old_password(DEFAULT_PASSWORD)
        vm.submit()
        assert vm.error == ""
        assert vm.message == "密码修改成功"
        # 成功后输入框被清空
        assert vm.old_password == "" and vm.new_password == ""

        # 新密码确实生效
        again = LoginViewModel(container.auth_service, container.workspace_service)
        again.set_username(DEFAULT_USERNAME)
        again.set_password("brand-new")
        assert again.submit() is not None

    def test_logout_clears_session(self, container) -> None:
        login = LoginViewModel(container.auth_service, container.workspace_service)
        login.set_username(DEFAULT_USERNAME)
        login.set_password(DEFAULT_PASSWORD)
        login.submit()

        assert container.auth_service.current_session() is not None
        route = container.settings.logout()
        assert route == "/login"
        assert container.auth_service.current_session() is None


# ── 列表 ────────────────────────────────────────────────────


class TestListPanel:
    @pytest.fixture
    def vm(self, container) -> ListPanelViewModel:
        return ListPanelViewModel(container.workspace_service, container.settings_service)

    def test_sync_route_loads_items_and_redirects(self, vm) -> None:
        target = vm.sync_route("/chat")

        assert target is not None and target.startswith("/chat/")
        assert vm.items  # 已载入条目

    def test_sync_route_resets_search(self, vm) -> None:
        vm.sync_route("/chat/zhang")
        vm.set_query("李")
        assert len(vm.items) == 1

        vm.sync_route("/chat/li")
        assert vm.query == ""

    def test_search_filters_by_name_and_preview(self, vm) -> None:
        vm.sync_route("/chat/zhang")

        vm.set_query("张三")
        assert [item.name for item in vm.items] == ["张三"]

        vm.set_query("不存在的关键词")
        assert vm.items == ()

    def test_resize_is_clamped(self, vm) -> None:
        layout = container_layout(vm)
        start = vm.width

        vm.resize_by(10_000)
        assert vm.width == layout.list_max

        vm.resize_by(-10_000)
        assert vm.width == layout.list_min

        vm.resize_by(0)
        assert vm.width != start or layout.list_min == layout.list_max

    def test_toggle_pin_changes_order(self, vm) -> None:
        vm.sync_route("/chat/zhang")
        before = [item.id for item in vm.items]

        vm.activate("toggle_pin", before[0])
        vm.sync_route("/chat/zhang")
        assert vm.items[0].is_pinned is True

    def test_hide_selected_item_returns_next_route(self, vm) -> None:
        vm.sync_route("/chat/zhang")
        selected = vm.selected_item_id

        target = vm.activate("hide", selected)

        assert target is not None
        assert selected not in [item.id for item in vm.items]

    def test_delete_non_selected_item_keeps_route(self, vm) -> None:
        vm.sync_route("/chat/zhang")
        other = next(i.id for i in vm.items if i.id != vm.selected_item_id)

        assert vm.activate("delete", other) is None
        assert other not in [item.id for item in vm.items]


def container_layout(vm: ListPanelViewModel):
    """读取视图模型使用的布局配置（用于断言区间）。"""
    return vm._settings.layout()


# ── 会话与搜索 ──────────────────────────────────────────────


class TestShellAndSearch:
    def test_tabs_are_created_once(self, container) -> None:
        shell: ShellViewModel = container.shell
        login = LoginViewModel(container.auth_service, container.workspace_service)
        login.set_username(DEFAULT_USERNAME)
        login.set_password(DEFAULT_PASSWORD)
        login.submit()

        shell.sync_location("/chat/zhang")
        shell.sync_location("/chat/zhang")

        assert len(shell.tabs) == 1
        assert shell.tabs[0].title == "张三"

    def test_settings_route_creates_tab(self, container) -> None:
        shell: ShellViewModel = container.shell
        login = LoginViewModel(container.auth_service, container.workspace_service)
        login.set_username(DEFAULT_USERNAME)
        login.set_password(DEFAULT_PASSWORD)
        login.submit()

        shell.sync_location("/settings")
        assert [tab.title for tab in shell.tabs] == ["设置"]

    def test_close_active_tab_navigates_to_neighbour(self, container) -> None:
        shell: ShellViewModel = container.shell
        login = LoginViewModel(container.auth_service, container.workspace_service)
        login.set_username(DEFAULT_USERNAME)
        login.set_password(DEFAULT_PASSWORD)
        login.submit()

        shell.sync_location("/chat/zhang")
        shell.sync_location("/chat/li")
        shell.sync_location("/chat/li")

        target = shell.close_tab("/chat/li")
        assert target == "/chat/zhang"

    def test_close_inactive_tab_does_not_navigate(self, container) -> None:
        shell: ShellViewModel = container.shell
        login = LoginViewModel(container.auth_service, container.workspace_service)
        login.set_username(DEFAULT_USERNAME)
        login.set_password(DEFAULT_PASSWORD)
        login.submit()

        shell.sync_location("/chat/zhang")
        shell.sync_location("/chat/li")
        assert shell.close_tab("/chat/zhang") is None

    def test_unauthenticated_requires_login(self, container) -> None:
        assert container.shell.sync_location("/chat/zhang") == "/login"

    def test_search_results_only_when_open(self, container) -> None:
        vm: SearchOverlayViewModel = container.search_overlay
        assert vm.results == ()

        vm.open()
        vm.set_query("张三")
        names = [item.name for item in vm.results]
        # 搜索同时匹配名称与预览：产品部的预览里也含「张三」
        assert "张三" in names
        assert "产品部" in names

        vm.close()
        assert vm.results == () and vm.query == ""


# ── 聊天与主题 ──────────────────────────────────────────────


class TestChatAndTheme:
    def test_send_message_appends_and_clears_draft(self, container) -> None:
        vm: ChatDetailViewModel = container.chat_detail
        vm.load("zhang")
        before = len(vm.messages)

        vm.set_draft("  新消息内容  ")
        vm.send()

        assert len(vm.messages) == before + 1
        assert vm.messages[-1].text == "新消息内容"
        assert vm.draft == ""

    def test_send_blank_is_ignored(self, container) -> None:
        vm: ChatDetailViewModel = container.chat_detail
        vm.load("zhang")
        before = len(vm.messages)

        vm.set_draft("   ")
        vm.send()

        assert len(vm.messages) == before

    def test_theme_apply_notifies_subscribers(self, container) -> None:
        theme: ThemeState = container.theme
        calls: list[int] = []
        theme.subscribe(lambda: calls.append(1))

        theme.apply_colors({"accent": "#123456"})

        assert calls == [1]
        assert theme.colors.accent == "#123456"
        # 已持久化：重新读取仍然生效
        assert container.settings_service.reload().colors.accent == "#123456"
