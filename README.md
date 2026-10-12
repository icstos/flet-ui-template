# CSTOS

Enterprise collaboration desktop application built with Flet, featuring chat, contacts, and email modules.

## Features

- **Chat Module**: Real-time messaging with bubble-style chat interface
- **Contacts**: Department and contact browsing
- **Email**: Email list and detail viewing
- **Theme Customization**: Customizable accent color, sidebar color, background, and more
- **Frameless Window**: Custom title bar with drag, minimize, maximize, and close support
- **Responsive Layout**: List panel width can be freely adjusted by dragging

## Tech Stack

- **UI Framework**: [Flet](https://flet.dev/) >= 1.0.4, < 2
- **Database**: SQLite + [SQLModel](https://sqlmodel.tiangolo.com/) >= 0.0.22
- **Configuration**: TOML config file + dataclass typed loading
- **Python Version**: >= 3.12

## Architecture

MVVM with strict layered dependency inversion. Dependencies flow in one
direction only — `View -> ViewModel -> Service -> Infra` — and every layer may
use `Models`. High-level layers depend on **abstractions**, never on concrete
technology.

| Layer | Responsibility | May import |
| --- | --- | --- |
| `models` | Entities, enums, constants, route value objects, reactive primitives. No business logic, no I/O. | `models` |
| `infra` | Wraps technology (TOML, SQLite, JSON, hashing) behind `Protocol` interfaces defined in `infra/protocols.py`. | `models`, `infra` |
| `service` | Orchestrates business use cases against those interfaces. | `models`, `infra.protocols`, `service` |
| `viewmodel` | Pure-Python UI state. Calls services, notifies subscribers. **Zero Flet imports.** | `models`, `service`, `viewmodel` |
| `view` | Declarative Flet components. Renders state, dispatches events. No business logic. | `models`, `viewmodel`, `view` |

UI is a pure function of state (`UI = f(state)`). A `ViewModel` extends
`Observable`; `view/hooks.py::use_view_model` subscribes a component to a
view model, and any state change re-renders it. Theme changes therefore apply
instantly without reload hacks.

`container.py` is the composition root (the only place that knows which
concrete implementation satisfies each interface) and `main.py` is the entry
point. Neither is part of the five layers.

## Project Structure

```
cs-ui-template/
├── models/                  # Layer 1 — data structures, no logic, no I/O
│   ├── entities.py          # Module / Item / Message / User (SQLModel)
│   ├── enums.py             # ModuleId, MessageRole
│   ├── settings.py          # AppSettings and its four sections
│   ├── route.py             # WorkspaceRoute value object
│   ├── reactive.py          # Observable (state + notify)
│   ├── session.py           # AuthSession value object
│   └── constants.py         # Color presets, routes, font constants
├── infra/                   # Layer 2 — technology behind protocols
│   ├── protocols.py         # SettingsStore / SessionStore / repositories / hasher
│   ├── config_store.py      # TOML read & write
│   ├── database.py          # Engine, session, schema migration
│   ├── seed.py              # Demo data + default account
│   ├── workspace_repository.py
│   ├── user_repository.py
│   ├── auth_store.py        # Login-state JSON persistence
│   └── password_hasher.py   # PBKDF2-HMAC-SHA256
├── service/                 # Layer 3 — business use cases
│   ├── auth_service.py      # Login / register / change password / logout
│   ├── workspace_service.py # Modules, items, messages, search, pin, hide, delete
│   └── settings_service.py  # Read / update / persist configuration
├── viewmodel/               # Layer 4 — pure-Python UI state
│   ├── base.py              # ViewModel + RouteTarget convention
│   ├── theme.py             # ThemeState (global reactive palette)
│   ├── shell.py             # Tabs + auth guard
│   ├── title_bar.py         # Maximize flag, hovered button
│   ├── nav_rail.py          # Modules, session, active module
│   ├── list_panel.py        # Items, query, width, context-menu actions
│   ├── chat_detail.py       # Messages + draft
│   ├── generic_detail.py    # Detail body
│   ├── search_overlay.py    # Open flag, query, results
│   ├── settings.py          # Editable colours, save / restore / logout
│   └── auth.py              # Login / register / change-password forms
├── view/                    # Layer 5 — declarative Flet components
│   ├── hooks.py             # use_view_model: the only state->render bridge
│   ├── contexts.py          # Container injection
│   ├── app.py               # Root view + route tree
│   ├── shell.py             # Title bar + nav rail + content + search
│   ├── title_bar.py         # Custom frameless title bar
│   ├── tab_bar.py           # Tab strip
│   ├── nav_rail.py          # Side navigation rail
│   ├── workspace.py         # List + detail two-column layout
│   ├── list_panel.py        # List, search, context menu, drag resize
│   ├── detail_chat.py       # Chat bubbles + composer
│   ├── detail_generic.py    # Scrolling detail body
│   ├── search_overlay.py    # Global search dialog
│   ├── settings.py          # Settings page
│   ├── auth.py              # Login / register / change-password views
│   ├── icons.py             # Icon-name resolution
│   └── widgets/             # Presentational-only widgets (avatar, detail panel)
├── tests/                   # Automated tests
│   ├── test_architecture.py # Enforces the layering rules above
│   ├── test_viewmodel.py    # Business behaviour, no UI required
│   ├── test_flet_smoke.py   # Renders every component offline
│   └── manual/              # Real-window verification scripts
├── container.py             # Composition root
├── main.py                  # Entry point
└── config.toml              # Configuration file
```


## Installation

### Option 1: pip install (Recommended)

```bash
pip install -e .
```

### Option 2: Manual dependency installation

```bash
pip install flet>=0.85.0 sqlmodel>=0.0.22
```

## Running

```bash
python main.py
```

## Configuration

Configuration file is located at [config.toml](config.toml), with the following sections:

### \[layout] - Layout Configuration

| Field          | Type | Default | Description                    |
| -------------- | ---- | ------- | ------------------------------ |
| `nav_width`    | int  | 68      | Side navigation bar width (px) |
| `list_min`     | int  | 200     | List panel minimum width (px)  |
| `list_max`     | int  | 480     | List panel maximum width (px)  |
| `list_default` | int  | 300     | List panel default width (px)  |
| `title_bar_h`  | int  | 40      | Title bar height (px)          |

### \[window] - Window Configuration

| Field        | Type | Default                    | Description           |
| ------------ | ---- | -------------------------- | --------------------- |
| `title`      | str  | "CSTOS"                    | Window title          |
| `subtitle`   | str  | "Enterprise Collaboration" | Window subtitle       |
| `width`      | int  | 1180                       | Default window width  |
| `height`     | int  | 720                        | Default window height |
| `min_width`  | int  | 920                        | Minimum window width  |
| `min_height` | int  | 520                        | Minimum window height |
| `frameless`  | bool | true                       | Use frameless window  |

### \[colors] - Color Theme

| Field              | Description                       |
| ------------------ | --------------------------------- |
| `sidebar`          | Sidebar background color          |
| `sidebar_hover`    | Sidebar hover color               |
| `sidebar_active`   | Sidebar active/selected color     |
| `accent`           | Theme accent color                |
| `accent_soft`      | Soft accent color                 |
| `list_bg`          | List background color             |
| `content_bg`       | Content area background color     |
| `border`           | Border color                      |
| `text`             | Primary text color                |
| `text_sec`         | Secondary text color              |
| `title_bar`        | Title bar background color        |
| `search_bg`        | Search box background color       |
| `icon_inactive`    | Inactive icon color               |
| `window_btn_icon`  | Window button icon color          |
| `title_text`       | Title bar text color              |
| `title_subtitle`   | Title bar subtitle color          |
| `input_bg`         | Input field background color      |
| `chat_self_bg`     | Self chat bubble background color |
| `chat_self_border` | Self chat bubble border color     |

### \[database] - Database Configuration

| Field | Type | Default                   | Description             |
| ----- | ---- | ------------------------- | ----------------------- |
| `url` | str  | "sqlite:///data/cstos.db" | Database connection URL |

## Data Models

### Module (Feature Module)

| Field         | Type | Description              |
| ------------- | ---- | ------------------------ |
| `id`          | str  | Unique module identifier |
| `label`       | str  | Display name             |
| `icon`        | str  | Unselected icon name     |
| `icon_filled` | str  | Selected icon name       |
| `sort_order`  | int  | Sort order               |

### Item (List Entry)

| Field          | Type | Description             |
| -------------- | ---- | ----------------------- |
| `id`           | str  | Unique item identifier  |
| `module_id`    | str  | Parent module ID        |
| `name`         | str  | Item name               |
| `subtitle`     | str  | Subtitle                |
| `preview`      | str  | Preview text            |
| `time`         | str  | Time display            |
| `color`        | str  | Avatar background color |
| `detail_title` | str  | Detail page title       |
| `detail_body`  | str  | Detail page content     |

### Message (Chat Message)

| Field        | Type | Description                  |
| ------------ | ---- | ---------------------------- |
| `id`         | int  | Auto-increment ID            |
| `item_id`    | str  | Parent item ID               |
| `role`       | str  | Message role (`me` / `them`) |
| `text`       | str  | Message content              |
| `sort_order` | int  | Sort order                   |

## Development

### Running Tests

```bash
pytest tests/                      # Architecture rules + view models + component rendering
python tests/manual/startup_check.py   # Launch the real app and report runtime errors
python tests/manual/render_check.py    # Screenshot the window and detect Flutter grey blocks
python tests/manual/theme_check.py     # Drive a real theme change and verify it applies
```

`tests/test_architecture.py` statically enforces the layering rules, so a
layering violation fails the suite instead of silently rotting.

### Adding a New Module

1. Add a `Module` record in `infra/seed.py`
2. Add the route in `view/app.py` and a view model in `viewmodel/`
3. Register the view model in `container.py`

### Customizing Theme

Click the settings button in the bottom-left corner to adjust accent, sidebar,
content background and text colour. Pressing "Save" writes `config.toml` and
pushes the new palette into `ThemeState`, which re-renders every subscribed
view immediately — no restart and no navigation required.

## License

MIT
