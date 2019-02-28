FROM node:8.14.1-alpine as node_container
COPY . /code
WORKDIR /code
RUN npm install && npm run build

FROM swaggerapi/swagger-ui:latest
ENV SWAGGER_JSON=/etc/api.yaml
COPY --from=node_container /code/result.yaml /etc/api.yaml

CMD ["sh", "/usr/share/nginx/run.sh"]
