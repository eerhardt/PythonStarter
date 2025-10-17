from __future__ import annotations

import contextlib
import datetime
import json
import logging
import os
import random
from typing import TYPE_CHECKING

import fastapi
import fastapi.responses
import fastapi.staticfiles
import opentelemetry.instrumentation.fastapi as otel_fastapi
import opentelemetry.instrumentation.redis as otel_redis
import redis
import telemetry

if TYPE_CHECKING:
    from typing import Literal, TypedDict

    type WeatherSummary = Literal[
        "Freezing",
        "Bracing",
        "Chilly",
        "Cool",
        "Mild",
        "Warm",
        "Balmy",
        "Hot",
        "Sweltering",
        "Scorching",
    ]

    class Forecast(TypedDict):
        date: str
        temperatureC: int
        temperatureF: int
        summary: WeatherSummary

    type RedisClient = redis.Redis | None


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    telemetry.configure_opentelemetry()
    yield


app: fastapi.FastAPI = fastapi.FastAPI(lifespan=lifespan)
otel_fastapi.FastAPIInstrumentor.instrument_app(app, exclude_spans=["send"])

# Global to store Redis client instance.
redis_client: RedisClient = None
otel_redis.RedisInstrumentor().instrument()


def get_redis_client() -> RedisClient:
    """Get the Redis client instance."""
    global redis_client
    if redis_client is None:
        if cache_uri := os.environ.get("CACHE_URI"):
            try:
                redis_client = redis.from_url(
                    cache_uri,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    decode_responses=True,
                )
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                redis_client = None
        else:
            logger.info(
                "No CACHE_URI environment variable found, Redis caching disabled"
            )
    return redis_client


logger: logging.Logger = logging.getLogger(__name__)


@app.get("/api/weatherforecast")
async def weather_forecast(
    redis_client: RedisClient = fastapi.Depends(get_redis_client),
) -> list[Forecast]:
    """Weather forecast endpoint."""
    cache_key = "weatherforecast"
    cache_ttl = 5  # 5 seconds cache duration

    # Try to get data from cache.
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info("Returning cached weather forecast data")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Redis cache read error: {e}")

    # Generate fresh data if not in cache or cache unavailable.
    # Make sure to keep WeatherSummary in sync.
    summaries = [
        "Freezing",
        "Bracing",
        "Chilly",
        "Cool",
        "Mild",
        "Warm",
        "Balmy",
        "Hot",
        "Sweltering",
        "Scorching",
    ]

    forecast = []
    for index in range(1, 6):  # Range 1 to 5 (inclusive)
        temp_c = random.randint(-20, 55)
        forecast_date = datetime.datetime.now() + datetime.timedelta(days=index)
        forecast_item = {
            "date": forecast_date.isoformat(),
            "temperatureC": temp_c,
            "temperatureF": int(temp_c * 9 / 5) + 32,
            "summary": random.choice(summaries),
        }
        forecast.append(forecast_item)

    # Cache the data.
    if redis_client:
        try:
            redis_client.setex(cache_key, cache_ttl, json.dumps(forecast))
        except Exception as e:
            logger.warning(f"Redis cache write error: {e}")

    return forecast


@app.get("/health", response_class=fastapi.responses.PlainTextResponse)
async def health_check(
    redis_client: RedisClient = fastapi.Depends(get_redis_client),
) -> Literal["Healthy"]:
    """Health check endpoint."""
    if redis_client:
        redis_client.ping()
    return "Healthy"


app.mount(
    "/",
    fastapi.staticfiles.StaticFiles(directory="static", html=True, check_dir=False),
    name="static",
)


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8111))
    host = os.environ.get("HOST", "127.0.0.1")
    reload = os.environ.get("DEBUG", "False").lower() == "true"

    uvicorn.run("app:app", host=host, port=port, reload=reload, log_level="info")
