ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:14.0.2
FROM ${BUILD_FROM}

ENV LANG=C.UTF-8

RUN apk add --no-cache nodejs npm

RUN python -m pip install --no-cache-dir --retries 5 --timeout 120 --index-url https://pypi.org/simple \
    fastapi uvicorn[standard] suncalc pytz geopy paho-mqtt astral websockets

WORKDIR /app
COPY web /app/web
RUN cd /app/web && npm install && npm run build

RUN mkdir -p /app/static && cp -r /app/web/dist/* /app/static/

COPY backend /app/backend
COPY config.yaml /app/config.yaml

EXPOSE 1980
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "1980"]
