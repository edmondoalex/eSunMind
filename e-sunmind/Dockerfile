ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:14.0.2
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

WORKDIR /app
COPY backend /app/backend
COPY web /app/web
COPY config.yaml /app/config.yaml

RUN pip install --no-cache-dir fastapi uvicorn[standard] suncalc pytz geopy paho-mqtt

EXPOSE 1977
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "1977"]
