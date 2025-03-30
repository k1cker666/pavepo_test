FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

COPY --from=ghcr.io/astral-sh/uv:0.6.9 /uv /uvx /bin/

ADD . /pavepo_test

WORKDIR /pavepo_test

RUN uv sync --frozen

ENV PATH="/pavepo_test/.venv/bin:$PATH"

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "80"]