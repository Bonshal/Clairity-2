import asyncio
from src.db.neon import async_session, ContentItemModel, TrendSignalModel, SentimentResultModel
from sqlalchemy import select, func

async def check_db():
    async with async_session() as s:
        # Check Content Items
        content_count = await s.scalar(select(func.count(ContentItemModel.id)))
        print(f"Total Content Items: {content_count}")
        
        platforms = await s.execute(select(ContentItemModel.platform, func.count(ContentItemModel.id)).group_by(ContentItemModel.platform))
        for p, c in platforms:
            print(f" - {p}: {c}")

        # Check Trend Signals
        trend_count = await s.scalar(select(func.count(TrendSignalModel.id)))
        print(f"\nTotal Trend Signals: {trend_count}")
        
        trends = await s.execute(select(TrendSignalModel.direction, func.count(TrendSignalModel.id)).group_by(TrendSignalModel.direction))
        for d, c in trends:
            print(f" - {d}: {c}")

        # Check Sentiment Results
        sentiment_count = await s.scalar(select(func.count(SentimentResultModel.id)))
        print(f"\nTotal Sentiment Results: {sentiment_count}")

if __name__ == "__main__":
    asyncio.run(check_db())
