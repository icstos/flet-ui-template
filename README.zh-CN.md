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

- **UI 框架**：[Flet](https://flet.dev/) >= 0.85.0
- **数据库**：SQLite + [SQLModel](https://sqlmodel.tiangolo.com/) >= 0.0.22
- **配置管理**：TOML 配置文件 + dataclass 类型化加载
- **Python 版本**：>= 3.9

## 项目结构

```
test_template/
├── components/          # 可复用 UI 组件
│   ├── avatar.py        # 圆形头像组件
│   ├── detail_panel.py  # 详情面板组件
│   └── title_bar.py     # 自定义标题栏
├── database/            # 数据库层
│   └── __init__.py      # 引擎、会话管理、初始化与种子数据
├── models/              # 数据模型
│   └── __init__.py      # Module / Item / Message 模型定义
├── my_utils/            # 工具函数
│   ├── icons.py         # 图标名称映射
│   └── route.py         # 路由路径解析
├── services/            # 业务逻辑层
│   └── repository.py    # 数据访问封装
├── views/               # 页面视图
│   ├── app.py           # 根路由配置
│   ├── shell.py         # 外壳布局（标题栏 + 导航）
│   ├── nav_rail.py      # 侧边导航栏
│   ├── workspace.py     # 工作区布局（列表 + 详情）
│   ├── list_panel.py    # 列表面板
│   ├── detail_chat.py   # 聊天详情页
│   ├── detail_generic.py# 通用详情页
│   └── settings.py      # 设置页面
├── config.py            # 配置加载与管理
├── config.toml          # 配置文件
├── theme.py             # 主题常量
├── main.py              # 应用入口
└── pyproject.toml       # 项目配置
```

## 安装

### 方式一：pip 安装（推荐）

```bash
pip install -e .
```

### 方式二：使用依赖文件

```bash
pip install flet>=0.85.0 sqlmodel>=0.0.22
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

### 添加新模块

1. 在数据库种子数据中添加新的 `Module` 记录
2. 在 [views/app.py](views/app.py) 中添加对应的路由配置
3. 如需要自定义详情页，创建对应的视图组件

### 自定义主题

在应用内点击左下角设置按钮，可调整：

- 主颜色
- 侧栏色
- 内容背景
- 文字色

点击「保存」后配置会写入 `config.toml` 并立即生效。

## License

MIT
