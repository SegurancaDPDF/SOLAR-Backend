#!/bin/bash

GITTAG="${1:-latest}"
SCALE="${2:-1}"

# 1. Atualize o projeto:
git fetch --tags --force # atualize as tags do sistema
git checkout origin/master # alterne para uma tag diferente da latest (para forçar a atualização)
git checkout ${GITTAG} # alterne para a tag latest

# 2. Crie as imagens com os arquivos atualizados do sistema:
docker-compose build python
docker-compose build web
docker-compose build

# 3. Execute este comando para atualizar a estrutura do banco de dados:
docker-compose run --rm web python manage.py migrate

# 4. Execute este comando para atualizar os grupos de permissão:
docker-compose run --rm web python manage.py criar_permissoes_padrao

# 5. Execute o docker compose, ele criará os containers e executará a aplicação na porta 8001:
docker-compose up -d --scale web=${SCALE} --remove-orphans

# 6. Execute este comando para forçar a atualização dos arquivos JS
docker-compose run --rm web python manage.py constance set JSVERSION $(date +%d%m%Y%H%M%S)

# 7. Execute estes comandos para forçar a limpeza dos caches
docker-compose run --rm web python manage.py clear_cache
docker-compose run --rm web python manage.py invalidate all
