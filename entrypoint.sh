#!/bin/bash
/etc/init.d/nginx start
uwsgi --ini /app/src/uwsgi/solar-socket.ini
