import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())

from database import patent_engine


async def deep_inspect():
    print("--- Deep Inspecting US Patent Tables ---")
    tables_to_check = [
        "us_patent_inventor",
        "us_patent_assignee",
        "us_patent_classification",
        "us_patent_text",
        "us_patent_master",
    ]

    async with patent_engine.connect() as conn:
        for table in tables_to_check:
            print(f"\n[DDL: {table}]")
            try:
                # SHOW CREATE TABLE returns (Table, Create Table)
                result = await conn.execute(text(f"SHOW CREATE TABLE {table}"))
                row = result.fetchone()
                if row:
                    print(row[1])
            except Exception as e:
                print(f"Error getting DDL for {table}: {e}")

    await patent_engine.dispose()


if __name__ == "__main__":
    asyncio.run(deep_inspect())
