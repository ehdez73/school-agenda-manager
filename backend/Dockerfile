FROM python:3.13-slim

RUN pip install uv

WORKDIR /app/backend

COPY backend/pyproject.toml backend/uv.lock* ./

RUN uv sync --locked --python /usr/local/bin/python3.13

COPY backend/ ./backend/
COPY docs/ ./docs/

EXPOSE 5000

CMD ["sh", "-c", "uv run flask --app backend.app run --host 0.0.0.0 --port 5000 "]