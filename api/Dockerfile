FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM base AS development
RUN npm ci
COPY . .
CMD ["npx", "nodemon", "--exec", "ts-node", "src/index.ts"]

FROM base AS production
COPY . .
RUN npm ci && npx tsc
CMD ["node", "dist/index.js"]
