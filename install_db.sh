#!/bin/bash

# schema do banco
# python manage.py migrate sites
# python manage.py migrate sessions
# python manage.py migrate admin
# python manage.py migrate reversion

# python manage.py migrate djcelery 0002 --fake

git checkout 22.03.1

python manage.py migrate auth
python manage.py migrate djcelery 0001
python manage.py migrate djcelery 0002 --fake
python manage.py migrate

git checkout master
python manage.py migrate

# dados iniciais
python manage.py loaddata bem
python manage.py loaddata estruturamoradia
python manage.py loaddata profissao
python manage.py loaddata deficiencia
python manage.py loaddata documento
python manage.py loaddata pais
python manage.py loaddata estado
python manage.py loaddata municipio
python manage.py loaddata cartorio

# papéis e permissões padrão
python manage.py criar_papeis_e_permissoes_padrao

# usuario administrador
python manage.py createsolarsuperuser --email admin@admin.com --user admin --password admin
