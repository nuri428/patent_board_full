import sys
import os
import asyncio
import importlib
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

from app.models import User

shared_database = importlib.import_module("shared.database")
mariadb_engine = shared_database.mariadb_engine
mariadb_session_factory = shared_database.mariadb_session_factory

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_users():
    print("Creating initial users...")

    default_user_password = os.getenv("INITIAL_USER_PASSWORD")
    default_admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")

    if not default_user_password or not default_admin_password:
        raise RuntimeError(
            "Set INITIAL_USER_PASSWORD and INITIAL_ADMIN_PASSWORD before running this script"
        )

    users_to_create = [
        {
            "username": "nuri",
            "password": default_user_password,
            "email": "greennuri@gmail.com",
            # "full_name": "Nuri",
            "is_admin": False,
        },
        {
            "username": "admin",
            "password": default_admin_password,
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

            password_value = user_data.get("password")
            if not isinstance(password_value, str):
                raise RuntimeError(
                    f"Password for {user_data['username']} must be a string"
                )

            print(f"Hashing password for {user_data['username']}...")
            try:
                # Bypass passlib and use bcrypt directly due to version incompatibility
                salt = bcrypt.gensalt()
                hashed_bytes = bcrypt.hashpw(password_value.encode("utf-8"), salt)
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
