import asyncio
import sys
import os
from sqlalchemy import text

sys.path.append(os.getcwd())

from database import patent_engine


async def inspect_patent_db():
    print("--- Inspecting Patent DB Schema ---")
    async with patent_engine.connect() as conn:
        try:
            # List tables
            print("\n[Tables]")
            result = await conn.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            for table in tables:
                table_name = table[0]
                print(f"- {table_name}")

            # Describe each table
            for table in tables:
                table_name = table[0]
                print(f"\n[Schema: {table_name}]")
                result = await conn.execute(text(f"DESCRIBE {table_name}"))
                rows = result.fetchall()
                print(f"{'Field':<25} {'Type':<20} {'Null':<10} {'Key':<10}")
                print("-" * 70)
                for row in rows:
                    print(
                        f"{str(row[0]):<25} {str(row[1]):<20} {str(row[2]):<10} {str(row[3]):<10}"
                    )

        except Exception as e:
            print(f"Error inspecting patent db: {e}")

    await patent_engine.dispose()


if __name__ == "__main__":
    asyncio.run(inspect_patent_db())
