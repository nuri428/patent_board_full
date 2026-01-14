import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())

from database import auth_engine


async def inspect():
    print("--- Inspecting Table Schema ---")
    async with auth_engine.connect() as conn:
        try:
            result = await conn.execute(text("DESCRIBE mcp_api_keys"))
            rows = result.fetchall()
            print(
                f"{'Field':<20} {'Type':<20} {'Null':<10} {'Key':<10} {'Default':<20}"
            )
            print("-" * 80)
            for row in rows:
                # row is a tuple, typically (Field, Type, Null, Key, Default, Extra)
                print(
                    f"{str(row[0]):<20} {str(row[1]):<20} {str(row[2]):<10} {str(row[3]):<10} {str(row[4]):<20}"
                )
        except Exception as e:
            print(f"Error inspecting table: {e}")

    await auth_engine.dispose()


if __name__ == "__main__":
    asyncio.run(inspect())
