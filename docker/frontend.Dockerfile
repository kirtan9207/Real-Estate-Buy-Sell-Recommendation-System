FROM node:20-slim

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

# Copy source
COPY frontend/ .

EXPOSE 5173

# Fix the host so it can be reached outside container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
