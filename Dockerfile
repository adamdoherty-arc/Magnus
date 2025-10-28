FROM node:18-alpine

# Create app directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs data exports backups

# Expose port (if needed for future web interface)
EXPOSE 3000

# Default command
CMD ["node", "src/app.js", "scan"]