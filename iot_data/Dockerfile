# Use an official Node.js runtime as the base image
FROM node:18-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package.json package-lock.json ./

# Remove existing node_modules and package-lock.json before installing dependencies
RUN rm -rf node_modules package-lock.json && npm install --legacy-peer-deps

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE 5173

# Define the command to run the application
CMD ["npm", "run", "dev"]
