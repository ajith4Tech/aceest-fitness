FROM python:3.12-slim

WORKDIR /app

RUN useradd --create-home appuser

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ACEest_Fitness.py .
COPY tests/ tests/

RUN chown -R appuser:appuser /app


USER appuser

ARG APP_VERSION=1.0.0
ENV APP_VERSION=$APP_VERSION

EXPOSE 5000

CMD ["python", "ACEest_Fitness.py"]

