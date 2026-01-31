FROM python:3.13-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim AS runner

# Create non-root user
RUN groupadd -g 1001 python && \
    useradd -u 1001 -g python python

WORKDIR /app

# Copy installed packages AND executables from builder stage
COPY --from=builder /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=python:python . .

# Switch to non-root user
USER python

EXPOSE 7860

HEALTHCHECK CMD curl -f http://localhost:7860/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--proxy-headers"]