# Install uv
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

# Install the project into `/app`
WORKDIR /app

# Disable development dependencies
ENV UV_NO_DEV=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project


# Copy the project into the image
COPY ./src /app/src

COPY pyproject.toml uv.lock /app/

# Sync the project into a new environment, asserting the lockfile is up to date
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked
EXPOSE 8050
# CMD ["uv", "run", "src.main:main"]
CMD ["uv", "run", "gunicorn", "--chdir", "src", "-b", "0.0.0.0:8050", "main:server"]