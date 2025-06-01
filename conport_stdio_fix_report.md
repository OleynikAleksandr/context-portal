# ConPort MCP stdio Mode Fix Report

## Issue

When starting the ConPort MCP server in `stdio` mode, a `NameError: name 'ensure_alembic_files_exist' is not defined` occurs.
This error appears because the function `ensure_alembic_files_exist` is called in `src/context_portal_mcp/main.py` (line 862 at the time of detection) before its module is imported in all code paths.

## Root Cause

The function `ensure_alembic_files_exist` was imported only in the main `try` block:

```python
# src/context_portal_mcp/main.py
try:
    from .handlers import mcp_handlers
    from .db import database, models
    from .db.database import ensure_alembic_files_exist
    from .core import exceptions
except ImportError:
    # ... fallback imports ...
```

However, in the `fallback` branch (the `except ImportError` block), which is used when the module is imported using system/absolute paths (for example, when running from an IDE or using `-m`), this import was missing. As a result, `ensure_alembic_files_exist` was not defined in this scope before its use, causing a `NameError`.

## Fix

The missing import was added into the `except ImportError` block in `src/context_portal_mcp/main.py`:

```python
# src/context_portal_mcp/main.py
# ...
except ImportError:
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from src.context_portal_mcp.handlers import mcp_handlers
    from src.context_portal_mcp.db import database, models
    from src.context_portal_mcp.core import exceptions
    from src.context_portal_mcp.db.database import ensure_alembic_files_exist  # <-- Added here
```

This line should appear together with the other imports in the `except` branch (immediately after `from src.context_portal_mcp.core import exceptions`).

## Verification Steps

1. Create or update the virtual environment (`venv`).
2. Install dependencies: `pip install -e .` or `uv pip install -e .`
3. Run the server in stdio mode:

    ```bash
    python -m src.context_portal_mcp.main --mode stdio --workspace_id .
    ```

After applying the fix, the server initializes correctly without a `NameError`, and the STDIO transport responds to requests as intended.

---

Report compiled by Roo, AI Assistant.
