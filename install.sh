#!/bin/bash

CRIARBANCO="${1:-false}"
YMLSUFFIX="${2:-http}"
GITTAG="${3:-latest}"

# 1. Atualize o projeto:
git fetch --tags # atualize as tags do sistema
git checkout $GITTAG # alterne para a tag especificada

# 2. Baixa e instala biblioteca para gerar arquivos PDF:
wget http://box.defensoria.to.def.br/medias/226/download -O wkhtmltox.tar.xz # baixa arquivo compactado
tar --extract -f wkhtmltox.tar.xz # extrai arquivo compactado
mkdir -p data
sudo mv binarios_executaveis data/wkhtmltox # move para local visível ao Docker
rm wkhtmltox.tar.xz # remove arquivo compactado

# 3. Crie as imagens do projeto:
docker-compose build

# 4. Execute este comando APENAS para um banco de dados limpo (vai criar a estrutura inicial):
if [ $CRIARBANCO == 'true'  ]
then
docker-compose run --rm web /bin/bash -c "source install_db.sh"
fi

# 5. Copia configuração para o docker-compose (padrão: http)
cp docker/docker-compose.override.${YMLSUFFIX}.yml docker-compose.override.yml

# 6. Execute o docker compose, ele criará os containers e executará a aplicação na porta 80:
docker-compose up -d --build
