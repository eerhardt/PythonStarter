import os
import logging
import random
import json
import datetime
from typing import List, Dict, Any, Optional
import fastapi
import fastapi.responses
import opentelemetry.trace
import opentelemetry.exporter.otlp.proto.grpc.trace_exporter
import opentelemetry.sdk.trace
import opentelemetry.sdk.trace.export
import opentelemetry.instrumentation.fastapi
import opentelemetry.instrumentation.redis
import redis

app = fastapi.FastAPI()

# Initialize Redis client
redis_client: Optional[redis.Redis] = None

def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        cache_uri = os.environ.get('CACHE_URI')
        if cache_uri:
            try:
                redis_client = redis.from_url(
                    cache_uri,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    decode_responses=True
                )
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                redis_client = None
        else:
            logger.info("No CACHE_URI environment variable found, Redis caching disabled")
    return redis_client

opentelemetry.trace.set_tracer_provider(opentelemetry.sdk.trace.TracerProvider())
otlpExporter = opentelemetry.exporter.otlp.proto.grpc.trace_exporter.OTLPSpanExporter()
processor = opentelemetry.sdk.trace.export.BatchSpanProcessor(otlpExporter)
opentelemetry.trace.get_tracer_provider().add_span_processor(processor)

opentelemetry.instrumentation.fastapi.FastAPIInstrumentor.instrument_app(app, exclude_spans=["send"])
opentelemetry.instrumentation.redis.RedisInstrumentor().instrument()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/api/weatherforecast", response_model=List[Dict[str, Any]])
async def weather_forecast():
    """Weather forecast endpoint"""
    cache_key = "weatherforecast"
    cache_ttl = 5  # 5 seconds cache duration

    # Try to get data from cache
    redis_client = get_redis_client()
    if redis_client:
        try:
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info("Returning cached weather forecast data")
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Redis cache read error: {e}")

    # Generate fresh data if not in cache or cache unavailable
    summaries = ["Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"]

    forecast = []
    for index in range(1, 6):  # Range 1 to 5 (inclusive)
        temp_c = random.randint(-20, 55)
        forecast_item = {
            'date': (datetime.datetime.now() + datetime.timedelta(days=index)).strftime('%Y-%m-%d'),
            'temperatureC': temp_c,
            'temperatureF': int(temp_c * 9/5) + 32,
            'summary': random.choice(summaries)
        }
        forecast.append(forecast_item)

    # Cache the data
    if redis_client:
        try:
            redis_client.setex(cache_key, cache_ttl, json.dumps(forecast))
        except Exception as e:
            logger.warning(f"Redis cache write error: {e}")

    return forecast

@app.get("/health", response_class=fastapi.responses.PlainTextResponse)
async def health_check():
    """Health check endpoint"""
    redis_client = get_redis_client()
    if redis_client:
        redis_client.ping()
    return "Healthy"

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 8111))
    host = os.environ.get('HOST', '127.0.0.1')
    reload = os.environ.get('DEBUG', 'False').lower() == 'true'

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
