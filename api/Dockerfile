# ─── Stage 1: Base ──────────────────────────────────────────
FROM node:20-alpine AS base
WORKDIR /app

# Copy manifests first (better layer caching)
COPY package*.json ./
# Prisma MUST be present before `npm ci` so postinstall can run `prisma generate`
COPY prisma/ ./prisma/


# ─── Stage 2: Development ───────────────────────────────────
FROM base AS development
RUN npm ci
COPY . .
EXPOSE 3001
CMD ["npx", "ts-node", "-r", "tsconfig-paths/register", "src/index.ts"]


# ─── Stage 3: Production ────────────────────────────────────
FROM base AS production
# Install all deps (including devDeps needed for tsc)
RUN npm ci
COPY . .
# Compile TypeScript and generate Prisma client
RUN npx prisma generate && npx tsc
# Prune dev dependencies after build
RUN npm prune --production

# Run as non-root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE 3001
CMD ["node", "dist/index.js"]
