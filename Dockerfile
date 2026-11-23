FROM python:3.9-slim

WORKDIR /app

RUN useradd --create-home appuser

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ACEest_Fitness.py .
COPY tests/ tests/

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

CMD ["python", "ACEest_Fitness.py"]

