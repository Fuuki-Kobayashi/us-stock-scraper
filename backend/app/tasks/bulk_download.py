import logging
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.data_sources.polygon_client import polygon_client
from app.models.collection_log import CollectionLog
from app.models.daily_price import DailyPrice
from app.models.dividend import Dividend
from app.models.stock_split import StockSplit
from app.models.ticker import Ticker

logger = logging.getLogger(__name__)

BATCH_COMMIT_SIZE = 10


# ---------------------------------------------------------------------------
# Daily Prices (grouped_daily)
# ---------------------------------------------------------------------------


async def _save_daily_prices(
    session: AsyncSession, target_date: date, results: list[dict]
) -> int:
    saved = 0
    for item in results:
        symbol = item.get("T", "")
        close = item.get("c")
        if not symbol or close is None:
            continue

        session.add(
            DailyPrice(
                symbol=symbol,
                trade_date=target_date,
                open=float(item.get("o", 0)),
                high=float(item.get("h", 0)),
                low=float(item.get("l", 0)),
                close=float(close),
                volume=int(item.get("v", 0)),
                vwap=float(item["vw"]) if item.get("vw") else None,
                transactions=int(item["n"]) if item.get("n") else None,
            )
        )
        saved += 1
    return saved


async def run_bulk_download(from_date: date, to_date: date) -> int:
    """Download all daily OHLCV data for a date range. Returns log ID."""
    async with async_session() as session:
        log = CollectionLog(job_type="bulk_download", status="running")
        session.add(log)
        await session.flush()
        log_id = log.id

        try:
            result = await session.execute(
                select(DailyPrice.trade_date)
                .where(
                    DailyPrice.trade_date >= from_date,
                    DailyPrice.trade_date <= to_date,
                )
                .distinct()
            )
            existing_dates = {row[0] for row in result.all()}

            total_records = 0
            days_processed = 0
            current_date = from_date

            while current_date <= to_date:
                if current_date.weekday() >= 5:
                    current_date += timedelta(days=1)
                    continue

                if current_date in existing_dates:
                    logger.info("Skipping %s (already downloaded)", current_date)
                    current_date += timedelta(days=1)
                    continue

                results = await polygon_client.grouped_daily(current_date)
                if results:
                    count = await _save_daily_prices(session, current_date, results)
                    total_records += count
                    days_processed += 1
                    logger.info(
                        "Bulk download %s: %d records (total: %d)",
                        current_date, count, total_records,
                    )
                    if days_processed % BATCH_COMMIT_SIZE == 0:
                        await session.commit()
                else:
                    logger.info("No data for %s (holiday?)", current_date)

                current_date += timedelta(days=1)

            log.status = "completed"
            log.records_count = total_records
            log.completed_at = datetime.utcnow()
            await session.commit()
            logger.info(
                "Bulk download completed (%s to %s): %d days, %d records",
                from_date, to_date, days_processed, total_records,
            )
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)[:500]
            log.completed_at = datetime.utcnow()
            await session.commit()
            logger.error("Bulk download failed: %s", e)
            raise

    return log_id


# ---------------------------------------------------------------------------
# Ticker Details Enrichment (per-ticker API)
# ---------------------------------------------------------------------------

TICKER_BATCH_COMMIT = 50


async def run_ticker_enrichment() -> int:
    """Enrich tickers with fundamentals from ticker_details API.

    Resume-aware: skips tickers that already have details_updated_at set.
    Returns log ID.
    """
    async with async_session() as session:
        log = CollectionLog(job_type="ticker_enrichment", status="running")
        session.add(log)
        await session.flush()
        log_id = log.id

        try:
            # Get tickers without details
            result = await session.execute(
                select(Ticker.symbol).where(Ticker.details_updated_at.is_(None))
            )
            symbols = [row[0] for row in result.all()]
            logger.info("Ticker enrichment: %d tickers to process", len(symbols))

            enriched = 0
            for i, symbol in enumerate(symbols):
                try:
                    details = await polygon_client.ticker_details(symbol)
                except Exception as e:
                    logger.warning("Failed to get details for %s: %s", symbol, e)
                    continue

                if details:
                    ticker_result = await session.execute(
                        select(Ticker).where(Ticker.symbol == symbol)
                    )
                    ticker = ticker_result.scalar_one_or_none()
                    if ticker:
                        ticker.market_cap = details.get("market_cap")
                        ticker.shares_outstanding = details.get(
                            "share_class_shares_outstanding"
                        )
                        ticker.weighted_shares_outstanding = details.get(
                            "weighted_shares_outstanding"
                        )
                        ticker.total_employees = details.get("total_employees")
                        ticker.description = details.get("description")
                        ticker.homepage_url = details.get("homepage_url")
                        ticker.primary_exchange = details.get("primary_exchange")
                        ticker.cik = details.get("cik")
                        list_date_str = details.get("list_date")
                        if list_date_str:
                            try:
                                ticker.list_date = date.fromisoformat(list_date_str)
                            except ValueError:
                                pass
                        ticker.sic_code = details.get("sic_code")
                        ticker.sic_description = details.get("sic_description")
                        ticker.details_updated_at = datetime.utcnow()
                        enriched += 1

                if (i + 1) % TICKER_BATCH_COMMIT == 0:
                    await session.commit()
                    logger.info(
                        "Ticker enrichment progress: %d/%d (%d enriched)",
                        i + 1, len(symbols), enriched,
                    )

            log.status = "completed"
            log.records_count = enriched
            log.completed_at = datetime.utcnow()
            await session.commit()
            logger.info("Ticker enrichment completed: %d/%d enriched", enriched, len(symbols))
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)[:500]
            log.completed_at = datetime.utcnow()
            await session.commit()
            logger.error("Ticker enrichment failed: %s", e)
            raise

    return log_id


# ---------------------------------------------------------------------------
# Dividends (paginated, all tickers at once)
# ---------------------------------------------------------------------------


async def run_dividends_download() -> int:
    """Download all dividend data via paginated API. Returns log ID."""
    async with async_session() as session:
        log = CollectionLog(job_type="dividends_download", status="running")
        session.add(log)
        await session.flush()
        log_id = log.id

        try:
            # Get existing dividend count for resume detection
            existing_count_result = await session.execute(
                select(func.count(Dividend.id))
            )
            existing_count = existing_count_result.scalar() or 0

            total = 0
            cursor = None
            page = 0

            while True:
                data = await polygon_client.dividends(cursor=cursor)
                results = data["results"]
                if not results:
                    break

                for item in results:
                    ticker = item.get("ticker", "")
                    ex_date_str = item.get("ex_dividend_date")
                    if not ticker or not ex_date_str:
                        continue

                    try:
                        ex_date = date.fromisoformat(ex_date_str)
                    except ValueError:
                        continue

                    session.add(
                        Dividend(
                            symbol=ticker,
                            cash_amount=float(item.get("cash_amount", 0)),
                            currency=item.get("currency"),
                            declaration_date=(
                                date.fromisoformat(item["declaration_date"])
                                if item.get("declaration_date")
                                else None
                            ),
                            ex_dividend_date=ex_date,
                            frequency=item.get("frequency"),
                            pay_date=(
                                date.fromisoformat(item["pay_date"])
                                if item.get("pay_date")
                                else None
                            ),
                            record_date=(
                                date.fromisoformat(item["record_date"])
                                if item.get("record_date")
                                else None
                            ),
                            dividend_type=item.get("dividend_type"),
                        )
                    )
                    total += 1

                page += 1
                await session.commit()
                logger.info(
                    "Dividends page %d: %d records (total: %d)",
                    page, len(results), total,
                )

                cursor = data.get("next_cursor")
                if not cursor:
                    break

            log.status = "completed"
            log.records_count = total
            log.completed_at = datetime.utcnow()
            await session.commit()
            logger.info("Dividends download completed: %d records", total)
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)[:500]
            log.completed_at = datetime.utcnow()
            await session.commit()
            logger.error("Dividends download failed: %s", e)
            raise

    return log_id


# ---------------------------------------------------------------------------
# Stock Splits (paginated, all tickers at once)
# ---------------------------------------------------------------------------


async def run_splits_download() -> int:
    """Download all stock split data via paginated API. Returns log ID."""
    async with async_session() as session:
        log = CollectionLog(job_type="splits_download", status="running")
        session.add(log)
        await session.flush()
        log_id = log.id

        try:
            total = 0
            cursor = None
            page = 0

            while True:
                data = await polygon_client.splits(cursor=cursor)
                results = data["results"]
                if not results:
                    break

                for item in results:
                    ticker = item.get("ticker", "")
                    exec_date_str = item.get("execution_date")
                    if not ticker or not exec_date_str:
                        continue

                    try:
                        exec_date = date.fromisoformat(exec_date_str)
                    except ValueError:
                        continue

                    # Skip duplicates
                    existing = await session.execute(
                        select(StockSplit).where(
                            StockSplit.symbol == ticker,
                            StockSplit.execution_date == exec_date,
                        )
                    )
                    if existing.scalar_one_or_none():
                        continue

                    session.add(
                        StockSplit(
                            symbol=ticker,
                            execution_date=exec_date,
                            split_from=int(item.get("split_from", 1)),
                            split_to=int(item.get("split_to", 1)),
                        )
                    )
                    total += 1

                page += 1
                await session.commit()
                logger.info(
                    "Splits page %d: %d records (total: %d)",
                    page, len(results), total,
                )

                cursor = data.get("next_cursor")
                if not cursor:
                    break

            log.status = "completed"
            log.records_count = total
            log.completed_at = datetime.utcnow()
            await session.commit()
            logger.info("Splits download completed: %d records", total)
        except Exception as e:
            log.status = "failed"
            log.error_message = str(e)[:500]
            log.completed_at = datetime.utcnow()
            await session.commit()
            logger.error("Splits download failed: %s", e)
            raise

    return log_id
