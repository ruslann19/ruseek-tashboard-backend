FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./src ./src
COPY ./prompt_templates ./prompt_templates

EXPOSE 8000

ENV PYTHONPATH=/app/src
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
