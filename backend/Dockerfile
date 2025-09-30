FROM python:3.13-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN uv sync --locked --python /usr/local/bin/python3.13

COPY . .

EXPOSE 5000

CMD ["sh", "-c", "uv run flask --app app.py run --host 0.0.0.0 --port 5000 "]