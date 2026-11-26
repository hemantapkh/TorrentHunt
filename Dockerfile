# Must satisfy requires-python (>=3.14). With a matching interpreter,
# uv installs prebuilt wheels; never let it download a different Python, because then
# packages like scipy/numpy get compiled from source (minutes of CPU, GBs of disk).
FROM python:3.14-slim
ENV UV_PYTHON_DOWNLOADS=never

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /opt/torrenthunt

RUN apt-get -y update

COPY app app
COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --frozen --all-groups

# Migrate the database schema first, then start the bot.
CMD ["sh", "-c", "uv run app/migrate.py && exec uv run app/main.py"]
