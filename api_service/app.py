import os
import logging
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import redis

app = FastAPI()

# Initialize Redis client
redis_client: Optional[redis.Redis] = None

def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        cache_uri = os.environ.get('CACHE_URI')
        if cache_uri:
            try:
                redis_client = redis.from_url(cache_uri, decode_responses=True)
                logger.info(f"Connected to Redis at {cache_uri}")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                redis_client = None
        else:
            logger.info("No CACHE_URI environment variable found, Redis caching disabled")
    return redis_client

trace.set_tracer_provider(TracerProvider())
otlpExporter = OTLPSpanExporter()
processor = BatchSpanProcessor(otlpExporter)
trace.get_tracer_provider().add_span_processor(processor)

FastAPIInstrumentor.instrument_app(app)

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
    logger.info("Generating fresh weather forecast data")
    summaries = ["Freezing", "Bracing", "Chilly", "Cool", "Mild", "Warm", "Balmy", "Hot", "Sweltering", "Scorching"]
    
    forecast = []
    for index in range(1, 6):  # Range 1 to 5 (inclusive)
        temp_c = random.randint(-20, 55)
        forecast_item = {
            'date': (datetime.now() + timedelta(days=index)).strftime('%Y-%m-%d'),
            'temperatureC': temp_c,
            'temperatureF': int(temp_c * 9/5) + 32,
            'summary': random.choice(summaries)
        }
        forecast.append(forecast_item)
    
    # Cache the data
    if redis_client:
        try:
            redis_client.setex(cache_key, cache_ttl, json.dumps(forecast))
            logger.info(f"Cached weather forecast data for {cache_ttl} seconds")
        except Exception as e:
            logger.warning(f"Redis cache write error: {e}")
    
    return forecast

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