import asyncio
from sqlalchemy import select, func
from src.db.neon import async_session, ContentItemModel

async def check_counts():
    async with async_session() as session:
        # Count by platform
        stmt = select(
            ContentItemModel.platform, 
            func.count(ContentItemModel.id)
        ).group_by(ContentItemModel.platform)
        
        result = await session.execute(stmt)
        print("--- Content Counts by Platform ---")
        for row in result.all():
            print(f"{row[0]}: {row[1]}")
            
        # Check total
        stmt_total = select(func.count(ContentItemModel.id))
        total = await session.execute(stmt_total)
        print(f"Total Items: {total.scalar()}")

if __name__ == "__main__":
    asyncio.run(check_counts())
