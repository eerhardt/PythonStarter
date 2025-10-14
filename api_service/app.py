import os
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()

trace.set_tracer_provider(TracerProvider())
otlpExporter = OTLPSpanExporter()
processor = BatchSpanProcessor(otlpExporter)
trace.get_tracer_provider().add_span_processor(processor)

FastAPIInstrumentor.instrument_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/weatherforecast", response_model=List[Dict[str, Any]])
async def weather_forecast():
    """Weather forecast endpoint"""
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