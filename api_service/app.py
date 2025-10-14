import os
import logging
import random
from datetime import datetime, timedelta
import flask
from flask import jsonify
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

app = flask.Flask(__name__)

trace.set_tracer_provider(TracerProvider())
otlpExporter = OTLPSpanExporter()
processor = BatchSpanProcessor(otlpExporter)
trace.get_tracer_provider().add_span_processor(processor)

FlaskInstrumentor().instrument_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/weatherforecast')
def weather_forecast():
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
    return jsonify(forecast)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8111))
    debug = bool(os.environ.get('DEBUG', False))
    host = os.environ.get('HOST', '127.0.0.1')
    app.run(port=port, debug=debug, host=host, use_reloader=True)