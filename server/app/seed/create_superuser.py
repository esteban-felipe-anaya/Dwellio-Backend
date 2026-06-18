"""Create or promote a staff superuser.

python -m app.seed.create_superuser --email admin@dwellio.app --password password
"""

from __future__ import annotations

import argparse
import asyncio

from sqlalchemy import select

from app.core.db import SessionLocal, create_all
from app.core.config import settings
from app.core.security import hash_password, new_id
from app.models import User


async def run(email: str, password: str, name: str) -> None:
    if settings.is_sqlite:
        await create_all()
    async with SessionLocal() as db:
        user = (
            await db.execute(select(User).where(User.email == email.lower()))
        ).scalar_one_or_none()
        if user is None:
            user = User(id=new_id("usr"), email=email.lower(), name=name)
            db.add(user)
        user.hashed_password = hash_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        await db.commit()
    print(f"Superuser ready: {email}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", default="admin@dwellio.app")
    parser.add_argument("--password", default="password")
    parser.add_argument("--name", default="Dwellio Admin")
    args = parser.parse_args()
    from app.core.event_loop import use_selector_event_loop

    use_selector_event_loop()
    asyncio.run(run(args.email, args.password, args.name))


if __name__ == "__main__":
    main()
