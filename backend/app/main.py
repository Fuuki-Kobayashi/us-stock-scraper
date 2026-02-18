import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models.ticker import Base
from app.routers import admin, settings, stocks, surges, tracking
from app.tasks.scheduler import scheduler, setup_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    setup_scheduler()
    scheduler.start()
    logger.info("Scheduler started")

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
