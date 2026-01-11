import sys
import os
import asyncio
from sqlalchemy import select
import bcrypt

# Monkeypatch bcrypt for passlib compatibility
# See https://github.com/pyca/bcrypt/issues/684
if not hasattr(bcrypt, "__about__"):

    class About:
        __version__ = bcrypt.__version__

    bcrypt.__about__ = About()

from passlib.context import CryptContext

# Add parent directory to path to allow importing shared
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

# Load .env from project root
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(env_path)

from shared.database import mariadb_engine, mariadb_session_factory
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_users():
    print("Creating initial users...")

    users_to_create = [
        {
            "username": "nuri",
            "password": "manhae",
            "email": "greennuri@gmail.com",
            # "full_name": "Nuri",
            "is_admin": False,
        },
        {
            "username": "admin",
            "password": "manhae",
            "email": "greennuri+admin@gmail.com",  # Modified to avoid unique constraint violation
            # "full_name": "Admin",
            "is_admin": True,
        },
    ]

    async with mariadb_session_factory() as session:
        for user_data in users_to_create:
            # Check if user exists
            stmt = select(User).where(User.username == user_data["username"])
            result = await session.execute(stmt)
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"User '{user_data['username']}' already exists. Skipping.")
                continue

            print(f"Hashing password for {user_data['username']}...")
            try:
                # Bypass passlib and use bcrypt directly due to version incompatibility
                salt = bcrypt.gensalt()
                hashed_bytes = bcrypt.hashpw(
                    user_data["password"].encode("utf-8"), salt
                )
                hashed_password = hashed_bytes.decode("utf-8")
            except Exception as e:
                print(f"Error hashing password: {e}")
                continue

            new_user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hashed_password,
                is_active=True,
                is_admin=user_data["is_admin"],
            )
            session.add(new_user)
            print(
                f"User '{user_data['username']}' created successfully (Email: {user_data['email']})."
            )

        await session.commit()

    await mariadb_engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_users())
