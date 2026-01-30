FROM node:20.9.0-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:20.9.0-alpine AS runner
RUN apk add --no-cache dumb-init

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --only=production

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Create non-root user
RUN addgroup -g 1001 -S nextjs && \
    adduser -S nextjs -u 1001

USER nextjs

EXPOSE 3000

ENV NEXT_TELEMETRY_DISABLED=1

HEALTHCHECK CMD wget -qO- http://localhost:3000 || exit 1

ENTRYPOINT ["dumb-init", "--"]
CMD ["node", ".next/standalone/server.js"]