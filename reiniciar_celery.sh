#!/bin/bash

if [[ $EUID = 0 ]]; then
        echo -e "\nIsto NAO deve ser executado como root" 2>&1
        echo -e "\n" 2>&1

        exit 1
fi


PROJECT_DIR_ABSOLUTE_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CURRENT_DIR="$(pwd)"

cd ${PROJECT_DIR_ABSOLUTE_PATH}

echo -e "Ativando virtualenv: ${PROJECT_DIR_ABSOLUTE_PATH}/../.env_solar2/"
source ${PROJECT_DIR_ABSOLUTE_PATH}/../.env_solar4/bin/activate

echo -e "\nSera solicitado a sua senha de root" 2>&1

sudo kill $(ps -ef | grep celery_task | grep -v grep | awk '{print $2}') > /dev/null 2>&1 || {
        echo "deu pau matar celery_task. processo inexistente";

}
sudo kill -9 $(ps -ef | grep flower | grep -v grep | awk '{print $2}') > /dev/null 2>&1 || {
        echo "deu pau matar flower. processo inexistente";

}
sudo kill $(ps -ef | grep beat | grep -v grep | awk '{print $2}') > /dev/null 2>&1 || {
        echo "deu pau matar beat. processo inexistente";

}


echo "reiniciando celery";
flower -A celery_task --logging=error --port=5555 &

python manage.py celerybeat -f ../log/sisat.log -l ERROR &

python manage.py celery worker -A celery_task -n prioridade-1.%h -l ERROR -f ../log/sisat.log --queue=prioridade &
python manage.py celery worker -A celery_task -n default-1.%h -l ERROR -f ../log/sisat.log --queue=default &
python manage.py celery worker -A celery_task -n default-2.%h -l ERROR -f ../log/sisat.log --queue=default &
python manage.py celery worker -A celery_task -n default-3.%h -l ERROR -f ../log/sisat.log --queue=default &
python manage.py celery worker -A celery_task -n default-4.%h -l ERROR -f ../log/sisat.log --queue=default &

echo -e "\n\n\nconcluido.";
cd ${CURRENT_DIR}
