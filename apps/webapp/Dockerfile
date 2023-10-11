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
RUN turbo prune webapp --docker

# Add lockfile and package.json's of isolated subworkspace
FROM base AS installer

# Install pnpm with corepack
RUN corepack enable && corepack prepare pnpm@latest --activate
# Enable `pnpm add --global` on Alpine Linux by setting
# home location environment variable to a location already in $PATH
# https://github.com/pnpm/pnpm/issues/784#issuecomment-1518582235
ENV PNPM_HOME=/usr/local/bin

RUN apk add --no-cache libc6-compat
RUN apk update
WORKDIR /app

# First install the dependencies (as they change less often)
COPY .gitignore .gitignore
COPY --from=builder /app/out/json/ .
COPY --from=builder /app/out/pnpm-lock.yaml ./pnpm-lock.yaml
RUN pnpm install

# Build the project
COPY --from=builder /app/out/full/ .
RUN pnpm run build --filter=webapp...

FROM base AS runner
WORKDIR /app

# Don't run production as root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs
USER nextjs

COPY --from=installer /app/apps/webapp/next.config.js .
COPY --from=installer /app/apps/webapp/package.json .

# Automatically leverage output traces to reduce image size
# https://nextjs.org/docs/advanced-features/output-file-tracing
COPY --from=installer --chown=nextjs:nodejs /app/apps/webapp/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/apps/webapp/.next/static ./apps/webapp/.next/static
COPY --from=installer --chown=nextjs:nodejs /app/apps/webapp/public ./apps/webapp/public

CMD node apps/webapp/server.js