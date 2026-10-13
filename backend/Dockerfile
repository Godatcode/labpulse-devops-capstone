FROM python:3.12-alpine

LABEL org.opencontainers.image.source="https://github.com/Godatcode/labpulse-devops-capstone" \
      org.opencontainers.image.title="LabPulse API" \
      org.opencontainers.image.description="Equipment and incident API for campus labs"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && addgroup -S labpulse && adduser -S -G labpulse -u 10001 labpulse

COPY --chown=labpulse:labpulse app ./app
COPY --chown=labpulse:labpulse alembic ./alembic
COPY --chown=labpulse:labpulse alembic.ini entrypoint.sh ./
RUN chmod 755 entrypoint.sh

USER 10001:10001
EXPOSE 8000
CMD ["./entrypoint.sh"]
