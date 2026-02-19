import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select

from app.database import async_session, engine
from app.models.daily_price import DailyPrice  # noqa: F401 (register model)
from app.models.ticker import Base, Ticker
from app.routers import admin, settings, stocks, surges, tracking
from app.tasks.scheduler import scheduler, setup_scheduler
from app.tasks.ticker_sync import run_ticker_sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _initial_ticker_sync() -> None:
    """Run ticker sync if the tickers table is empty."""
    async with async_session() as session:
        result = await session.execute(select(func.count(Ticker.symbol)))
        count = result.scalar() or 0
    if count == 0:
        logger.info("Tickers table empty, running initial sync...")
        await run_ticker_sync()
        logger.info("Initial ticker sync completed")
    else:
        logger.info("Tickers table has %d records, skipping initial sync", count)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    setup_scheduler()
    scheduler.start()
    logger.info("Scheduler started")

    # Run initial ticker sync in background (non-blocking)
    asyncio.create_task(_initial_ticker_sync())

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")
    await engine.dispose()


app = FastAPI(
    title="US Stock Surge Analyzer",
    description="Detect and analyze US stocks with significant daily gains",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(surges.router)
app.include_router(tracking.router)
app.include_router(stocks.router)
app.include_router(settings.router)
app.include_router(admin.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
