FROM node:22-alpine

WORKDIR /app

# Copy package files first for caching
COPY front_end/package.json front_end/package-lock.json* ./

# Install dependencies
RUN npm install

# Copy application code
COPY front_end/ .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
