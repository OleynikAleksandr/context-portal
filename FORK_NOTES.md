# Заметки по форку ConPort (OleynikAleksandr/context-portal)

## Проблема: Автоматическая инициализация DB не создает таблицы

**Версия ConPort:** 0.2.4+fork.alembic_fixes (и последующие до этого исправления)

**Описание:**
При первом запуске ConPort в новом рабочем пространстве, несмотря на создание `alembic.ini`, директории `alembic/` и файла `context_portal/context.db`, таблицы базы данных (например, `product_context`, `decisions` и т.д.) не создавались. Это приводило к ошибкам "no such table" при попытках использования ConPort.

**Причина:**
Основная причина заключалась в том, что в состав пакета (в директорию шаблонов `src/context_portal_mcp/templates/alembic/alembic/versions/`) не были включены сами файлы скриптов миграций Alembic (`.py`), которые содержат инструкции по созданию таблиц. Функция `ensure_alembic_files_exist` копировала структуру директорий Alembic, но без скриптов миграций `command.upgrade(cfg, "head")` не мог создать таблицы. Дополнительно были выявлены и исправлены проблемы с путями и конфигурацией Alembic при автогенерации и выполнении миграций.

**Процесс исправления (ключевые шаги):**

1.  **Корректировка `ensure_alembic_files_exist` ([`src/context_portal_mcp/db/database.py`](src/context_portal_mcp/db/database.py:1)):**
    *   Функция была обновлена для рекурсивного копирования всего содержимого директории `src/context_portal_mcp/templates/alembic/alembic/` (включая поддиректорию `versions` с файлами миграций) в рабочее пространство пользователя (`[workspace_root]/alembic/`).

2.  **Корректировка `run_migrations` ([`src/context_portal_mcp/db/database.py`](src/context_portal_mcp/db/database.py:1)):**
    *   Установка `script_location` и `sqlalchemy.url` в объекте `Config` Alembic теперь использует абсолютные пути, разрешенные из `project_root_dir` (путь к рабочему пространству) и `db_path` соответственно. Это обеспечивает корректную работу Alembic независимо от текущей рабочей директории процесса.
    *   Добавлено более подробное логирование для отладки путей.

3.  **Создание и настройка шаблонов Alembic в пакете ConPort:**
    *   Поскольку оригинальные шаблоны Alembic отсутствовали в `src/context_portal_mcp/templates/alembic/`, они были созданы:
        *   `src/context_portal_mcp/templates/alembic/alembic.ini`
        *   `src/context_portal_mcp/templates/alembic/alembic/script.py.mako`
        *   `src/context_portal_mcp/templates/alembic/alembic/env.py`
    *   `alembic.ini` настроен с `script_location = %(here)s/alembic`.
    *   `env.py` модифицирован для корректного добавления путей в `sys.path` и импорта `Base.metadata` из нового файла `src.context_portal_mcp.db.orm_models`.

4.  **Создание ORM Моделей SQLAlchemy (`src/context_portal_mcp/db/orm_models.py`):**
    *   Создан новый файл `orm_models.py`, содержащий определения таблиц ConPort с использованием SQLAlchemy ORM и декларативную базу `Base = declarative_base()`. Это необходимо для работы `alembic revision --autogenerate`. На данный момент содержит базовые модели; требует дополнения всеми остальными таблицами.

5.  **Генерация начального файла миграции:**
    *   После всех вышеописанных настроек была успешно выполнена команда:
        ```bash
        # В директории context-portal, с настроенным PYTHONPATH
        python -m alembic -c src/context_portal_mcp/templates/alembic/alembic.ini revision -m "create_initial_conport_tables" --autogenerate
        ```
    *   Это создало файл миграции (`b7798b697008_create_initial_conport_tables.py`) в `src/context_portal_mcp/templates/alembic/alembic/versions/`.
    *   Шаблон `script.py.mako` был исправлен для корректной обработки `down_revision = None` при первой миграции.

**Результат:**
Теперь при первом запуске ConPort в новом рабочем пространстве:
1.  Все необходимые файлы Alembic, включая скрипты миграций из `versions/`, корректно копируются из шаблонов пакета в директорию `[workspace_root]/alembic/`.
2.  Функция `run_migrations` успешно применяет эти миграции к базе данных `[workspace_root]/context_portal/context.db`, создавая все необходимые таблицы.

**Дальнейшие шаги для разработчика форка:**
*   Дополнить `src/context_portal_mcp/db/orm_models.py` всеми остальными ORM-моделями, соответствующими Pydantic-моделям и предполагаемой схеме БД.
*   После дополнения `orm_models.py` **повторно сгенерировать миграцию** (`python -m alembic -c src/context_portal_mcp/templates/alembic/alembic.ini revision -m "название_новой_миграции" --autogenerate`), чтобы она включала все таблицы. Текущий сгенерированный файл (`b7798b697008_create_initial_conport_tables.py`) можно либо удалить перед новой полной генерацией, либо оставить, а Alembic создаст новую миграцию для добавления остальных таблиц.
*   Файл `.gitkeep` из `src/context_portal_mcp/templates/alembic/alembic/versions/` был перезаписан пустым содержимым и может быть удален при коммите (или оставлен, если это стандартная практика для пустых директорий в Git).
*   Тщательно протестировать инициализацию в чистом рабочем пространстве.
*   Закоммитить изменения, включая новые шаблоны Alembic и сгенерированный файл миграции.