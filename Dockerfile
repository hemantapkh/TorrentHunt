FROM python:3.12

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /opt/torrenthunt

RUN apt-get -y update

COPY app app
COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --frozen --all-groups

CMD ["uv", "run", "app/torrenthunt.py"]
