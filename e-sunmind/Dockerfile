ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:14.0.2
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

RUN apk add --no-cache nodejs npm

WORKDIR /app
COPY web /app/web
RUN cd /app/web && npm install && npm run build

RUN mkdir -p /app/static && cp -r /app/web/dist/* /app/static/

COPY backend /app/backend
COPY config.yaml /app/config.yaml

RUN pip install --no-cache-dir fastapi uvicorn[standard] suncalc pytz geopy paho-mqtt astral

EXPOSE 1977
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "1977"]
