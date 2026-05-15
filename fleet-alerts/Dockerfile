FROM python:3.12-slim

WORKDIR /app

RUN useradd -m appuser

COPY fleet_alerts.py /app/fleet_alerts.py
RUN pip install --no-cache-dir requests

RUN mkdir -p /data && chown -R appuser:appuser /data
VOLUME ["/data"]

USER appuser
CMD ["python", "/app/fleet_alerts.py"]
