#!/bin/sh

service cron start
crontab /etc/cron.d/cleanup-tmp

exec "$@"
