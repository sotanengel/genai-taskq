FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE /app/
COPY src /app/src

RUN pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "genai_taskq.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
