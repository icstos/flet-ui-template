# CSTOS

企业协作桌面应用，基于 Flet 框架构建，提供聊天、通讯录、邮箱等功能模块。

## 功能特性

- **聊天模块**：实时消息收发，支持气泡式聊天界面
- **通讯录**：部门和联系人浏览
- **邮箱**：邮件列表与详情查看
- **主题自定义**：支持自定义主题色、侧栏色、背景色等
- **无边框窗口**：自定义标题栏，支持拖动、最小化、最大化、关闭
- **响应式布局**：列表面板宽度可自由拖拽调整

## 技术栈

- **UI 框架**：[Flet](https://flet.dev/) >= 1.0.4, < 2
- **数据库**：SQLite + [SQLModel](https://sqlmodel.tiangolo.com/) >= 0.0.22
- **配置管理**：TOML 配置文件 + dataclass 类型化加载
- **Python 版本**：>= 3.12

## 架构

采用 MVVM + 严格分层依赖倒置。依赖**单向流动**：
`View -> ViewModel -> Service -> Infra`，且所有层都可依赖 `Models`。
高层只依赖**抽象接口**，不依赖具体技术实现。

| 层级 | 职责 | 允许导入 |
| --- | --- | --- |
| `models` | 实体、枚举、常量、路由值对象、响应式原语。无业务逻辑、无 IO。 | `models` |
| `infra` | 封装底层技术（TOML / SQLite / JSON / 哈希），并通过 `infra/protocols.py` 中的 `Protocol` 暴露抽象接口。 | `models`、`infra` |
| `service` | 编排业务流程，只针对抽象接口编程。 | `models`、`infra.protocols`、`service` |
| `viewmodel` | 纯 Python 的界面状态；调用业务服务并通知订阅者。**零 Flet 依赖。** | `models`、`service`、`viewmodel` |
| `view` | 声明式 Flet 组件：渲染状态、分发事件，无业务逻辑。 | `models`、`viewmodel`、`view` |

界面完全是状态的纯函数（`UI = f(state)`）。视图模型继承 `Observable`，
`view/hooks.py::use_view_model` 把组件订阅到视图模型，状态一变即重渲染。
因此换主题是即时生效的，不再需要重载模块或连续导航。

`container.py` 是组合根（唯一知道「抽象接口对应哪个具体实现」的地方），
`main.py` 是入口；两者都不属于五个层级。

## 项目结构

```
cs-ui-template/
├── models/                  # 第 1 层：数据结构，无逻辑、无 IO
│   ├── entities.py          # Module / Item / Message / User（SQLModel）
│   ├── enums.py             # ModuleId、MessageRole
│   ├── settings.py          # AppSettings 及四个配置节
│   ├── route.py             # WorkspaceRoute 值对象
│   ├── reactive.py          # Observable（状态 + 通知）
│   ├── session.py           # AuthSession 值对象
│   └── constants.py         # 预设色、路由、字体常量
├── infra/                   # 第 2 层：抽象接口背后的技术实现
│   ├── protocols.py         # SettingsStore / SessionStore / 仓库 / 哈希器
│   ├── config_store.py      # TOML 读写
│   ├── database.py          # 引擎、会话、结构迁移
│   ├── seed.py              # 演示数据 + 默认账号
│   ├── workspace_repository.py
│   ├── user_repository.py
│   ├── auth_store.py        # 登录态 JSON 持久化
│   └── password_hasher.py   # PBKDF2-HMAC-SHA256
├── service/                 # 第 3 层：业务用例
│   ├── auth_service.py      # 登录 / 注册 / 改密 / 登出
│   ├── workspace_service.py # 模块、条目、消息、搜索、置顶、隐藏、删除
│   └── settings_service.py  # 配置读取 / 更新 / 持久化
├── viewmodel/               # 第 4 层：纯 Python 界面状态
│   ├── base.py              # ViewModel 基类 + RouteTarget 约定
│   ├── theme.py             # ThemeState（全局响应式配色）
│   ├── shell.py             # 标签页 + 登录守卫
│   ├── title_bar.py         # 最大化标记、悬停按钮
│   ├── nav_rail.py          # 模块列表、当前用户、激活模块
│   ├── list_panel.py        # 条目、搜索词、宽度、右键菜单动作
│   ├── chat_detail.py       # 消息与草稿
│   ├── generic_detail.py    # 详情正文
│   ├── search_overlay.py    # 开关、关键词、结果
│   ├── settings.py          # 可编辑配色、保存 / 恢复 / 登出
│   └── auth.py              # 登录 / 注册 / 改密表单
├── view/                    # 第 5 层：声明式 Flet 组件
│   ├── hooks.py             # use_view_model：唯一的状态→渲染桥接
│   ├── contexts.py          # 容器注入
│   ├── app.py               # 根视图 + 路由树
│   ├── shell.py             # 标题栏 + 导航栏 + 内容区 + 搜索
│   ├── title_bar.py         # 自有标题栏（无边框窗口）
│   ├── tab_bar.py           # 标签条
│   ├── nav_rail.py          # 侧边导航栏
│   ├── workspace.py         # 列表 + 详情双栏布局
│   ├── list_panel.py        # 列表、搜索、右键菜单、拖动调宽
│   ├── detail_chat.py       # 消息气泡 + 输入栏
│   ├── detail_generic.py    # 可滚动详情正文
│   ├── search_overlay.py    # 全局搜索弹窗
│   ├── settings.py          # 设置页
│   ├── auth.py              # 登录 / 注册 / 改密视图
│   ├── icons.py             # 图标名解析
│   └── widgets/             # 纯展示控件（头像、详情面板）
├── tests/                   # 自动化测试
│   ├── test_architecture.py # 强制校验上述分层规则
│   ├── test_viewmodel.py    # 业务行为，无需启动 UI
│   ├── test_flet_smoke.py   # 离线渲染全部组件
│   └── manual/              # 真机窗口验证脚本
├── container.py             # 组合根
├── main.py                  # 应用入口
└── config.toml              # 配置文件
```


## 安装

### 方式一：pip 安装（推荐）

```bash
pip install -e .
```

### 方式二：使用依赖文件

```bash
pip install "flet>=1.0.4,<2" "sqlmodel>=0.0.22"
```

## 运行

```bash
python main.py
```

## 配置说明

配置文件位于 [config.toml](config.toml)，包含以下配置节：

### \[layout] - 布局配置

| 字段             | 类型  | 默认值 | 说明           |
| -------------- | --- | --- | ------------ |
| `nav_width`    | int | 68  | 侧边导航栏宽度（px）  |
| `list_min`     | int | 200 | 列表面板最小宽度（px） |
| `list_max`     | int | 480 | 列表面板最大宽度（px） |
| `list_default` | int | 300 | 列表面板默认宽度（px） |
| `title_bar_h`  | int | 40  | 标题栏高度（px）    |

### \[window] - 窗口配置

| 字段           | 类型   | 默认值     | 说明        |
| ------------ | ---- | ------- | --------- |
| `title`      | str  | "CSTOS" | 窗口标题      |
| `subtitle`   | str  | "企业协作"  | 窗口副标题     |
| `width`      | int  | 1180    | 窗口默认宽度    |
| `height`     | int  | 720     | 窗口默认高度    |
| `min_width`  | int  | 920     | 窗口最小宽度    |
| `min_height` | int  | 520     | 窗口最小高度    |
| `frameless`  | bool | true    | 是否使用无边框窗口 |

### \[colors] - 颜色主题

| 字段                 | 说明        |
| ------------------ | --------- |
| `sidebar`          | 侧边栏背景色    |
| `sidebar_hover`    | 侧边栏悬停色    |
| `sidebar_active`   | 侧边栏选中色    |
| `accent`           | 主题强调色     |
| `accent_soft`      | 柔和强调色     |
| `list_bg`          | 列表背景色     |
| `content_bg`       | 内容区背景色    |
| `border`           | 边框颜色      |
| `text`             | 主文字颜色     |
| `text_sec`         | 次要文字颜色    |
| `title_bar`        | 标题栏背景色    |
| `search_bg`        | 搜索框背景色    |
| `icon_inactive`    | 未激活图标颜色   |
| `window_btn_icon`  | 窗口按钮图标颜色  |
| `title_text`       | 标题栏文字颜色   |
| `title_subtitle`   | 标题栏副标题颜色  |
| `input_bg`         | 输入框背景色    |
| `chat_self_bg`     | 己方聊天气泡背景色 |
| `chat_self_border` | 己方聊天气泡边框色 |

### \[database] - 数据库配置

| 字段    | 类型  | 默认值                       | 说明        |
| ----- | --- | ------------------------- | --------- |
| `url` | str | "sqlite:///data/cstos.db" | 数据库连接 URL |

## 数据模型

### Module（功能模块）

| 字段            | 类型  | 说明     |
| ------------- | --- | ------ |
| `id`          | str | 模块唯一标识 |
| `label`       | str | 显示名称   |
| `icon`        | str | 未选中图标名 |
| `icon_filled` | str | 选中图标名  |
| `sort_order`  | int | 排序序号   |

### Item（列表条目）

| 字段             | 类型  | 说明      |
| -------------- | --- | ------- |
| `id`           | str | 条目唯一标识  |
| `module_id`    | str | 所属模块 ID |
| `name`         | str | 名称      |
| `subtitle`     | str | 副标题     |
| `preview`      | str | 预览文本    |
| `time`         | str | 时间显示    |
| `color`        | str | 头像背景色   |
| `detail_title` | str | 详情页标题   |
| `detail_body`  | str | 详情页正文   |

### Message（聊天消息）

| 字段           | 类型  | 说明                  |
| ------------ | --- | ------------------- |
| `id`         | int | 自增 ID               |
| `item_id`    | str | 所属条目 ID             |
| `role`       | str | 消息角色（`me` / `them`） |
| `text`       | str | 消息内容                |
| `sort_order` | int | 排序序号                |

## 开发

### 运行测试

```bash
pytest tests/                        # 分层规则 + 视图模型 + 组件渲染
python tests/manual/startup_check.py # 真实启动应用并捕获运行期异常
python tests/manual/render_check.py  # 截图窗口并检测 Flutter 灰块
python tests/manual/theme_check.py   # 驱动一次真实换肤并验证全局生效
```

`tests/test_architecture.py` 会静态校验分层规则，因此一旦出现跨层依赖，
测试会直接失败，而不是等到日后腐化。

### 添加新模块

1. 在 `infra/seed.py` 中添加 `Module` 记录
2. 在 `view/app.py` 中登记路由，并在 `viewmodel/` 中添加对应视图模型
3. 在 `container.py` 中完成装配

### 自定义主题

在应用内点击左下角设置按钮，可调整主颜色、侧栏色、内容背景与文字色。
点击「保存」后配置写入 `config.toml`，同时把新配色推入 `ThemeState`，
所有已订阅的视图立即重渲染——无需重启，也无需跳转。

## License

MIT
