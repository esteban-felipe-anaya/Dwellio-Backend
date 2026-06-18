"""Windows asyncio compatibility for psycopg.

psycopg's async mode cannot run on Windows' default ``ProactorEventLoop``; it
requires a ``SelectorEventLoop``. Call :func:`use_selector_event_loop` before
``asyncio.run`` in any process that opens an async PostgreSQL connection
(migrations, seed scripts, etc.). No-op on non-Windows / non-psycopg setups.
"""

from __future__ import annotations

import asyncio
import sys


def use_selector_event_loop() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
