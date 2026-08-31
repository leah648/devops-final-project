# Use a slim Python base image
FROM python:3.11-slim

# Do not buffer stdout/stderr
ENV PYTHONUNBUFFERED=1

# Create a group and user to avoid running as root
RUN groupadd --system appgroup && useradd --system --gid appgroup --create-home appuser

WORKDIR /app

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt ./

# Install build dependencies where necessary and install python deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy application source
COPY . /app

# Use non-root user
USER appuser

EXPOSE 5000

# Use gunicorn as the production server; expose WSGI app at module-level (app)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "2"]
