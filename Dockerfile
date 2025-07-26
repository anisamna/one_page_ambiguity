FROM python:3.9.18-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV=/ambiguity/.venv \
    PATH="/ambiguity/.venv/bin:$PATH"

WORKDIR /ambiguity

# Install dependencies & system tools in one RUN
RUN apt-get update -y && \
    apt-get install -y gcc postgresql-client curl && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and install uv
RUN pip install --upgrade pip uv

# Copy only pyproject first to leverage Docker layer caching
COPY pyproject.toml uv.lock* /ambiguity/

# Create virtualenv and install dependencies
RUN uv venv .venv && \
    uv pip install --upgrade pip && \
    uv sync

# Install pip and spacy model
RUN uv pip install pip && uv run python -m spacy download en_core_web_sm

# Copy the rest of the source code (this will be overridden by volume in dev)
COPY . /ambiguity

# Make script executable
RUN chmod +x wait-for-postgres.sh


# Use development server with auto-reload enabled
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8005"]