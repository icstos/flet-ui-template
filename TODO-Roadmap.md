


## 技术约束

- **Flet `>=1.0.5,<2`**，Python `>=3.12`。用 `ft.Button`（不是 `ElevatedButton`）、
  `ft.NoInputBorder()`（不是 `InputBorder.NONE`）。
- `page.padding` / `page.spacing` / `page.bgcolor` 在 1.x 已不存在，
  赋值**不报错但不生效**；页面背景用根视图的 `Container`，
  窗口底色用 `page.window.bgcolor`。
- `@ft.component` 组件只能由 `page.render()` 渲染，不能直接调用；
  `page.render()` 收的是组件函数本身。
- 全部类型注解，优先新语法（`X | None`、`list[T]`、PEP 695 泛型）。

## 架构红线（测试会强制校验）

依赖**单向**：`view -> viewmodel -> service -> infra`，所有层可依赖 `models`。
目录即分层：
- `models/` 无逻辑、无 IO，不依赖任何其它层。包括实体、枚举、常量、路由值对象、Observable等
- `infra/` 通过 `infra/protocols.py` 暴露 `Protocol`；实现放在各 `*_store` /
  `*_repository` 模块。
- `service/` **只**导入 `infra.protocols`，不得导入具体实现。
- `viewmodel/` **零 Flet 依赖**，纯 Python 类，不操作 UI 组件。
- `view/` 无业务逻辑，只渲染状态、分发事件。
- `container.py` 是唯一知道「接口→实现」映射的地方。
- 校验命令：`pytest tests/test_architecture.py`。

## 惯用写法

- **状态驱动渲染**：组件内 `vm = use_view_model(use_container().xxx)`，
  VM 状态变更 → `notify()` → 组件重渲染。禁止用 `importlib.reload` 或
  反复导航来强制刷新。
- **导航**：VM 方法返回目标路由字符串（`RouteTarget`），由 View 执行
  `ft.context.page.navigate(...)`。VM 内不得出现 `page.navigate`。
- **纯展示控件**放在 `view/widgets/`，配色等依赖由参数传入，不自行读状态。
- 组件内的 Hook 调用必须在任何提前 `return` 之前。
- 所有面向用户的文案统一使用中文。

## 已知坑

- `models/entities.py` 不能加 `from __future__ import annotations`，
  否则 SQLModel 的 Relationship 注解解析失败。
- 密码哈希格式 `salt$hash`（PBKDF2-SHA256，100000 次）**不可更改**，
  否则既有用户无法登录。
- 数据库表名由类名决定（`Module`→`module`），字段名即列名，不可随意改名。
- `data/cstos.db` 与 `data/auth.json` 是用户数据，测试须使用临时目录
  （见 `tests/conftest.py`）。
- `config.toml` 里的键名与 `models/settings.py` 字段名一一对应，不可改名。

## 验证习惯

改动后至少跑：

```bash
pytest tests/                          # 36 项自动化
python tests/manual/startup_check.py   # 真机启动
python tests/manual/render_check.py    # 截图 + 灰块检测
ruff check .
```

静态检查全绿**不等于**能跑：历史上有两个错误（`page.render` 上下文、
`Container(spacing=...)`）只有真机启动才暴露。
真机点击的坐标是**逻辑**坐标（物理像素 / DPI）。

## 真机点击坐标（tests/manual/）

- `probe_support.ROOT_PADDING ≈ 10.3`：Flet 内容相对客户区左上角的内边距。
  按布局公式算坐标要**加上**它，从截图上量坐标要**减去**它，否则稳定偏 10px。
- `probe_support.client_logical_size()` 取客户区尺寸；窗口矩形尺寸已删除勿再用。
- 验证截图用**程序化判据**（数特定颜色像素），不要靠 Read 工具看图——
  它会按内容去重，文件变了也可能显示旧图。
- 扫颜色边界用精确取值；`#f4f6f9` 与 `#F7F9FB` 仅差 3，容差稍大就混淆。
- 前几次点击可能被系统吃掉，坐标正确也可能一次不生效，需要重试。

## UI 尺寸调整

导航栏尺寸集中在 `view/nav_rail.py` 顶部的 `RAIL_*` 常量中，改栏宽时
按钮/图标/头像/设置键应同比收缩。外层 Column 必须设
`horizontal_alignment=CENTER`，否则子列会左对齐而非栏内居中。
`Container.width` 是内容宽度，水平 padding 会额外撑大占位。
