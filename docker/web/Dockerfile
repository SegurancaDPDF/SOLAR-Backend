ARG tag=latest
FROM gitlab.defensoria.to.def.br:5000/defensoria/sisat/python:$tag

COPY ./ /app/src/

WORKDIR /app/src

RUN mkdir -p /app/src/staticfiles_producao/

RUN python manage.py collectstatic_js_reverse

RUN python manage.py collectstatic --clear --noinput

RUN python manage.py compress --force

# RUN python manage.py clear_cache

# Crontab para limpar arquivos com mais de 2h de criação no diretório /tmp a cada 12h
COPY crontab_scripts/cleanup-tmp /etc/cron.d/cleanup-tmp
RUN chmod 0644 /etc/cron.d/cleanup-tmp
RUN ["chmod", "u+x", "/app/src/start-cron.sh"]

ENTRYPOINT ["sh", "/app/src/start-cron.sh"]

EXPOSE 1024

CMD ["uwsgi", "--ini", "/app/src/uwsgi/solar.ini"]
