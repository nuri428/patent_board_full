import asyncio
import sys
import os
from datetime import date

sys.path.append(os.getcwd())

from database import get_patent_db, patent_engine
from db.models import KRPatent, ForeignPatent
from sqlalchemy import select


async def test_retrieval():
    print("--- Testing Patent Retrieval ---")

    async for session in get_patent_db():
        try:
            # 1. Test Foreign Patent Search
            print("\n[1] Testing Foreign Patent Query...")
            stmt = select(ForeignPatent).limit(1)
            result = await session.execute(stmt)
            fp = result.scalar_one_or_none()

            if fp:
                print(f"Found Foreign Patent: {fp.document_number}")
                print(f"Title: {fp.invention_name}")
                if fp.raw_data:
                    print(f"Has Raw Data: Yes ({len(fp.raw_data)} chars)")
                else:
                    print("Has Raw Data: No")
            else:
                print("No Foreign Patents found (Database might be empty?)")

            # 2. Test KR Patent Search
            print("\n[2] Testing KR Patent Query...")
            stmt = select(KRPatent).limit(1)
            result = await session.execute(stmt)
            kp = result.scalar_one_or_none()

            if kp:
                print(f"Found KR Patent: {kp.application_number}")
                print(f"Title: {kp.title}")
            else:
                print("No KR Patents found.")

        except Exception as e:
            print(f"Error: {e}")

    await patent_engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_retrieval())
