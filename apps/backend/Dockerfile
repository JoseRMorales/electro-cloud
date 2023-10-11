FROM node:18-alpine AS base

FROM base AS builder
RUN apk add --no-cache libc6-compat
RUN apk update

# Install pnpm with corepack
RUN corepack enable && corepack prepare pnpm@latest --activate
# Enable `pnpm add --global` on Alpine Linux by setting
# home location environment variable to a location already in $PATH
# https://github.com/pnpm/pnpm/issues/784#issuecomment-1518582235
ENV PNPM_HOME=/usr/local/bin

# Set working directory
WORKDIR /app
RUN pnpm install -g turbo
COPY . .
RUN turbo prune backend --docker

FROM python:3.11

WORKDIR /app

COPY --from=builder /app/apps/backend/requirements.txt .

RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY --from=builder /app/apps/backend/app .

CMD ["uvicorn", "API.main:app", "--host", "0.0.0.0", "--port", "80"]
