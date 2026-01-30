FROM oven/bun:latest AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install all dependencies
RUN bun install

# Copy rest of the application
COPY frontend/. .

# Build the application
RUN bun run build

FROM oven/bun:latest AS runner
RUN apt-get update && apt-get install -y --no-install-recommends dumb-init && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install only production dependencies
RUN bun install --production

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Create non-root user
RUN groupadd -g 1001 -r nextjs && \
    useradd -u 1001 -r -g nextjs nextjs

USER nextjs

EXPOSE 3000

ENV NEXT_TELEMETRY_DISABLED=1

HEALTHCHECK CMD wget -qO- http://localhost:3000 || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["bun", "start"]