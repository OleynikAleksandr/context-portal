# Детальный список изменений в форке ConPort (OleynikAleksandr/context-portal)

## Цель: Автоматическая инициализация БД с созданием таблиц

**Дата последнего обновления:** 2025-06-01

---

### 1. Модуль `src.context_portal_mcp.db.database`

*   **`ensure_alembic_files_exist(workspace_root_dir: Path)`:**
    *   **Изменено:** Логика копирования шаблонов Alembic. Вместо простого копирования `alembic.ini` и директории `alembic/` (которая могла быть пустой или неполной в шаблонах), теперь функция использует `shutil.copytree` для рекурсивного копирования всего содержимого `src/context_portal_mcp/templates/alembic/alembic/` в `[workspace_root_dir]/alembic/`. Это включает `env.py`, `script.py.mako` и, что критично, поддиректорию `versions/` со всеми сгенерированными файлами миграций.
    *   Добавлена проверка и создание директории `versions` внутри `[workspace_root_dir]/alembic/`, если она не была создана `copytree`.

*   **`run_migrations(db_path: Path, project_root_dir: Path)`:**
    *   **Изменено:** Установка путей для `Config` Alembic.
        *   `alembic_ini_path`: теперь используется `.resolve()` для получения абсолютного пути.
        *   `alembic_scripts_path`: теперь используется `.resolve()` для получения абсолютного пути и передается в `cfg.set_main_option("script_location", str(alembic_scripts_path))`.
        *   `sqlalchemy.url`: теперь формируется с использованием `db_path.resolve()` для гарантии абсолютного пути: `f"sqlite:///{resolved_db_path}"`.
    *   **Добавлено:** Более подробное логирование для отладки используемых путей и конфигурации Alembic.
    *   **Добавлено:** Явная проверка существования `alembic.ini` и директории `alembic/versions` перед вызовом `command.upgrade`.

---

### 2. Шаблоны Alembic (`src.context_portal_mcp.templates.alembic`)

*   **Создана базовая структура шаблонов Alembic**, так как она отсутствовала:
    *   **`src/context_portal_mcp/templates/alembic/alembic.ini`:**
        *   Создан стандартный `alembic.ini`.
        *   `script_location` установлен в `%(here)s/alembic` для корректного разрешения пути после копирования в рабочее пространство.
        *   `sqlalchemy.url` установлен в `sqlite:///./placeholder_conport.db` (будет переопределен в `run_migrations`).
    *   **`src/context_portal_mcp/templates/alembic/alembic/script.py.mako`:**
        *   Создан стандартный `script.py.mako`.
        *   **Исправлено:** Выражение для `down_revision` изменено с `${down_revision | PythonLiteral}` на `${repr(down_revision)}` для корректной обработки первой миграции, где `down_revision` равен `None`.
    *   **`src/context_portal_mcp/templates/alembic/alembic/env.py`:**
        *   Создан стандартный `env.py`.
        *   **Изменено:** Модифицирована логика добавления путей в `sys.path` для более надежного обнаружения пакета `src` при запуске `alembic` из командной строки. Добавляются `GRANDPARENT_DIR` (родитель корня проекта) и `SRC_PARENT_DIR` (корень проекта).
        *   **Изменено:** `target_metadata` теперь импортируется из нового файла `src.context_portal_mcp.db.orm_models`:
            ```python
            from src.context_portal_mcp.db.orm_models import Base
            target_metadata = Base.metadata
            ```
    *   **`src/context_portal_mcp/templates/alembic/alembic/versions/`:**
        *   Создана директория (изначально с `.gitkeep`, который потом был перезаписан).
        *   **Добавлен файл миграции:** После всех настроек, с помощью команды `python -m alembic -c src/context_portal_mcp/templates/alembic/alembic.ini revision -m "create_initial_conport_tables" --autogenerate` был сгенерирован начальный файл миграции (`b7798b697008_create_initial_conport_tables.py`), который теперь является частью шаблонов.

---

### 3. Модели SQLAlchemy ORM (`src.context_portal_mcp.db.orm_models`)

*   **Создан новый файл `src/context_portal_mcp/db/orm_models.py`:**
    *   В нем определена `Base = declarative_base()`.
    *   Добавлены примеры ORM-моделей (`ProductContextORM`, `ActiveContextORM`, `DecisionORM`), соответствующие таблицам базы данных.
    *   **Требуется доработка:** Необходимо добавить ORM-определения для всех остальных таблиц ConPort (ProgressEntry, SystemPattern, CustomData, ContextLink, таблицы истории и т.д.), чтобы автогенерация Alembic могла их учитывать.

---

### 4. Исходный файл `src.context_portal_mcp.main` (исправление предыдущей ошибки)

*   В блоке `except ImportError` для fallback-импортов добавлен импорт `ensure_alembic_files_exist`:
    ```python
    from src.context_portal_mcp.db.database import ensure_alembic_files_exist
    ```
    Это исправило ошибку `NameError` при запуске сервера в STDIO-режиме, когда использовался fallback-путь импорта.

---

**Общий результат:**
После этих изменений, при условии, что `src/context_portal_mcp/db/orm_models.py` будет содержать полные определения всех таблиц и миграция будет перегенерирована для их включения, ConPort должен полностью автоматически создавать и настраивать базу данных со всеми таблицами при первом запуске в новом рабочем пространстве.
---

### 5. Дополнительные изменения (2025-06-01)

| Файл/компонент | Изменение |
| --- | --- |
| `src.context_portal_mcp.db.database` | • `_add_context_history_entry` — добавлен параметр **`context_id`** и логика выбора колонки (`product_context_id` / `active_context_id`).<br>• `update_product_context` и `update_active_context` передают `1` как `context_id`. |
| Начальный скрипт миграции | Исправленный `3d3360227021_create_initial_conport_tables_v2.py` включает:<br>• Таблицы истории `product_context_history`, `active_context_history` с колонками `timestamp`, `version`, `change_source`, ссылками на основные таблицы.<br>• Вставку начальных строк в `product_context` и `active_context`. |
| Шаблоны Alembic | В каталоге `templates/alembic/alembic/versions/` хранится **единственный** корректный файл миграции. |
| Чистка репозитория | Удалены корневые файлы-дубликаты (`3d3360227021_create_initial_conport_tables_v2.py`, `CONPORT_FULL_TEST_REPORT.md`). Коммит `b15e58b`. |

> После этих правок ConPort без ошибок инициализирует базу в чистом рабочем пространстве и корректно ведёт историю изменений контекстов.