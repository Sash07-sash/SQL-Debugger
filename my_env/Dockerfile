FROM python:3.11-slim

WORKDIR /app

COPY server/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

COPY . /app
RUN pip install --no-cache-dir -e .

ENV HOST=0.0.0.0
ENV PORT=8000

CMD ["uvicorn", "my_env.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
