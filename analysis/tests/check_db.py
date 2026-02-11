import asyncio
from src.db.neon import async_session, ContentItemModel
from sqlalchemy import select, func

async def check_db():
    async with async_session() as s:
        count = await s.scalar(select(func.count(ContentItemModel.id)))
        platforms = await s.execute(select(ContentItemModel.platform, func.count(ContentItemModel.id)).group_by(ContentItemModel.platform))
        
        print(f"Total items in DB: {count}")
        for p, c in platforms:
            print(f" - {p}: {c}")

if __name__ == "__main__":
    asyncio.run(check_db())
