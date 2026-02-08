import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())

from database import patent_engine


async def check_raw_data():
    print("--- Checking Raw Data Content ---")
    async with patent_engine.connect() as conn:
        try:
            result = await conn.execute(
                text("SELECT patent_number, raw_data FROM us_patent_master LIMIT 1")
            )
            row = result.fetchone()
            if row:
                print(f"Patent Number: {row[0]}")
                print(
                    f"Raw Data (First 500 chars): {row[1][:500] if row[1] else 'None'}"
                )
            else:
                print("No rows found in us_patent_master")
        except Exception as e:
            print(f"Error: {e}")

    await patent_engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_raw_data())
