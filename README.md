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

- **UI Framework**: [Flet](https://flet.dev/) >= 0.85.0
- **Database**: SQLite + [SQLModel](https://sqlmodel.tiangolo.com/) >= 0.0.22
- **Configuration**: TOML config file + dataclass typed loading
- **Python Version**: >= 3.9

## Project Structure

```
test_template/
├── components/          # Reusable UI components
│   ├── avatar.py        # Circular avatar component
│   ├── detail_panel.py  # Detail panel component
│   └── title_bar.py     # Custom title bar
├── database/            # Database layer
│   └── __init__.py      # Engine, session, initialization & seed data
├── models/              # Data models
│   └── __init__.py      # Module / Item / Message model definitions
├── my_utils/            # Utility functions
│   ├── icons.py         # Icon name mapping
│   └── route.py         # Route path parsing
├── services/            # Business logic layer
│   └── repository.py    # Data access layer
├── views/               # Page views
│   ├── app.py           # Root route configuration
│   ├── shell.py         # Shell layout (title bar + navigation)
│   ├── nav_rail.py      # Side navigation rail
│   ├── workspace.py      # Workspace layout (list + detail)
│   ├── list_panel.py     # List panel
│   ├── detail_chat.py    # Chat detail page
│   ├── detail_generic.py  # Generic detail page
│   └── settings.py       # Settings page
├── config.py             # Configuration loading & management
├── config.toml           # Configuration file
├── theme.py              # Theme constants
├── main.py               # Application entry point
└── pyproject.toml        # Project configuration
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

### Adding a New Module

1. Add a new `Module` record in the database seed data
2. Add corresponding route configuration in [views/app.py](views/app.py)
3. Create a custom detail view component if needed

### Customizing Theme

Click the settings button in the bottom-left corner to adjust:

- Accent color
- Sidebar color
- Content background
- Text color

After clicking "Save", the configuration will be written to `config.toml` and take effect immediately.

## License

MIT
