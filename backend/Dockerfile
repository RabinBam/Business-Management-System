# Stage 1: Build dependencies
FROM python:3.12-slim AS builder
WORKDIR /app

# Create a virtual environment and make sure we use it
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies into the venv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Run application
FROM python:3.12-slim

WORKDIR /app

# Copy the venv from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Ensure the venv is active by putting it first in PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code
COPY ./ /app/

# Create a non-root user and give them ownership of the app directory
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "-m", "app.demo_start"]
