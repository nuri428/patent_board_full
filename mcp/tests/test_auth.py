import asyncio
import sys
import os
from sqlalchemy import select, delete

sys.path.append(os.getcwd())

from database import get_auth_db, auth_engine
from auth.models import APIKey
from auth.security import verify_api_key


async def test_auth():
    print("--- Testing Authentication ---")

    test_key_str = "test-key-123456"  # Changed to avoid conflict if old one persists
    created_new_key = False

    async_session = get_auth_db()
    session = await anext(async_session)

    try:
        # 1. Check if key exists using new column name 'api_key'
        query = select(APIKey).where(APIKey.api_key == test_key_str)
        result = await session.execute(query)
        existing_key = result.scalar_one_or_none()

        if existing_key:
            print(f"Test key '{test_key_str}' already exists. Using existing key.")
        else:
            print("Inserting test key...")
            new_key = APIKey(
                api_key=test_key_str,
                name="Test Key",
                key_type="simple",  # key_type instead of role
                user_id=1,  # dummy user_id
                is_active=True,
            )
            session.add(new_key)
            await session.commit()
            created_new_key = True
            print("Test key inserted.")

        # 2. Verify Key
        print("Verifying key...")
        result_key = await verify_api_key(api_key_str=test_key_str, session=session)

        print(f"Verified Key: {result_key.name} (Type: {result_key.key_type})")
        assert result_key.api_key == test_key_str
        assert result_key.is_active == True
        print("Verification SUCCESS.")

    except Exception as e:
        print(f"Verification FAILED: {e}")
        raise
    finally:
        # Cleanup - Modified to respect user policy (No auto-deletion)
        print("\n--- Test Finished ---")
        if created_new_key:
            print(
                f"NOTE: A new test key '{test_key_str}' was created in mcp_api_keys with user_id=1."
            )
            print(f"Per safety policy, it was NOT automatically deleted.")
            print(
                f"To remove it, run SQL: DELETE FROM mcp_api_keys WHERE api_key = '{test_key_str}';"
            )
        else:
            print(f"Existing key '{test_key_str}' was used and left unchanged.")

        await session.close()
        await auth_engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_auth())
