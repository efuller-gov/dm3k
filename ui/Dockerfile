
# build stage
FROM node:12.14.0-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN yarn

# this should get the yarn.lock if its there
COPY . .

RUN yarn config set strict-ssl false 
RUN yarn run build

# Production stage
FROM nginx:1.16.1-alpine as production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD [ "nginx", "-g", "daemon off;"]
