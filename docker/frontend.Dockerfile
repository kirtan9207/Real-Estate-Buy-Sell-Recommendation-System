FROM node:20-slim

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

# Copy source
COPY frontend/ .

# Create non-root user and set ownership
RUN useradd -m -u 1000 -s /bin/bash tuf \
    && chown -R tuf:tuf /app

USER tuf

EXPOSE 5173

# Fix the host so it can be reached outside container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
