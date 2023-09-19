ARG tag=latest
FROM gitlab.defensoria.to.def.br:5000/defensoria/sisat/web:$tag

RUN apt update && apt install nginx -y

COPY docker/nginx/solar /etc/nginx/sites-enabled/default

RUN mkdir -p /app/logs/nginx/

RUN echo '' > /app/logs/nginx/solar-error.log

EXPOSE 1023

CMD ["/bin/bash", "./entrypoint.sh"]
