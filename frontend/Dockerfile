FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN npm cache clean --force && rm -rf node_modules package-lock.json && npm install --include=optional

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]