# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals  # isort:skip

# Biblioteca Padrao
from contextlib import contextmanager as _contextmanager

# Bibliotecas de terceiros
from fabric.api import cd, env, prefix, run, sudo

env.hosts = ["desenvolvimento@10.60.1.26"]
env.passwords = {"desenvolvimento@10.60.1.26": "sqlserver"}
env.directory = "/home/desenvolvimento/sisat/src"
env.activate = "source /home/desenvolvimento/.env/bin/activate"


@_contextmanager
def virtualenv():
    with cd(env.directory):
        with prefix(env.activate):
            yield


def deploy():
    with cd(env.directory):
        run("git reset --hard HEAD")
        run("git pull origin master")
        sudo("touch /etc/uwsgi/apps-available/sisat.ini")

    '''
    with virtualenv():
        run("./manage.py migrate")
    '''
