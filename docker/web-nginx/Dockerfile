ARG tag=latest
FROM gitlab.defensoria.to.def.br:5000/defensoria/sisat/python:$tag

RUN apt install nginx -y

COPY docker/web-nginx/solar /etc/nginx/sites-enabled/

COPY ./ /app/src/

WORKDIR /app/src

RUN mkdir -p /app/src/staticfiles_producao/

RUN python manage.py collectstatic_js_reverse

RUN python manage.py collectstatic --clear --noinput

RUN python manage.py compress --force

# RUN python manage.py clear_cache

EXPOSE 1023

CMD ["/bin/bash", "./entrypoint.sh"]
