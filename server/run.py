"""Dev server entrypoint.

On Windows, psycopg's async driver requires a SelectorEventLoop, but uvicorn
otherwise forces a ProactorEventLoop. This runner sets the SelectorEventLoop
policy and tells uvicorn not to override it (``loop="none"``). The autoreload
child process can't inherit that policy, so reload is disabled on Windows
(use SQLite for reload-heavy dev, or restart manually).

    python run.py
"""

from __future__ import annotations

import sys

import uvicorn

from app.core.event_loop import use_selector_event_loop

if __name__ == "__main__":
    is_windows = sys.platform == "win32"
    use_selector_event_loop()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # reachable from emulators / physical devices
        port=8000,
        reload=not is_windows,
        loop="none" if is_windows else "auto",
    )
