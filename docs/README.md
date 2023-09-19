# Instalando dependências do sistema operacional

```bash
sudo apt-get update
sudo apt-get install git-core curl --yes
```

## Instalando `apt-fast` (acelerador de downloads para `apt-get`)

```bash
/bin/bash -c "$(curl -sL https://git.io/vokNn)"
```

Se o download do arquivo acima não funcionar, execute o comando abaixo

```bash
#!/bin/bash
sudo apt-get install -y aria2 git
if ! [[ -f /usr/bin/apt-fast ]]; then
  git clone https://github.com/ilikenwf/apt-fast /tmp/apt-fast
  sudo cp /tmp/apt-fast/apt-fast /usr/bin
  sudo chmod +x /usr/bin/apt-fast
  sudo cp /tmp/apt-fast/apt-fast.conf /etc
fi
```

```bash
sudo apt-fast -y install python-dev-is-python3 gettext build-essential zlib1g-dev libpq-dev libtiff5-dev libjpeg-dev libfreetype6-dev liblcms2-dev libwebp-dev libmemcached-dev libssl-dev graphviz-dev memcached redis-server redis-tools sysvinit-utils
```

## Configurando `sysvinit`

```bash
echo -e "PATH=$PATH:/usr/sbin" >> ~/.bashrc

source ~/.bashrc
```

## Instalando o `pip` (gerenciador de pacotes python)

```bash
cd /tmp; wget https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py; sudo -H python2 get-pip.py -U; cd -
```

## Instalando `virtualenv` e `virtualenvwrapper`

```bash
sudo -H pip install virtualenv virtualenvwrapper
```


### Configurando VirtualEnvWrapper

```bash
echo -e "export WORKON_HOME=$HOME/.virtualenvs\nsource /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc

source ~/.bashrc
```

# Configurando o pip para utilizar cache

```bash
mkdir -p ~/.config/pip/

echo -e "[global]\nindex-url = http://root:test@pypi.defensoria.to.def.br:4040/root/pypi/+simple/\ntrusted-host = pypi.defensoria.to.def.br\nextra-index-url = https://pypi.python.org/simple" | tee ~/.config/pip/pip.conf
```

# Clonando projeto
```bash
cd $HOME

mkdir -p solar

cd solar

git clone https://lucas.mo@gitlab.defensoria.to.def.br/defensoria/sisat.git src
```

## Criando arquivos de log
```bash
mkdir -p log/nginx

touch log/sisat.log

touch log/nginx/{error.log,access.log}
```

## Configurando arquivo .env
```ini
DEBUG=False
TEMPLATE_DEBUG=False
SECRET_KEY=chave_randomica_extremamente_grande
DATABASE_URL=postgres://usuario_banco:senha_banco@ip_banco:porta_banco/nome_banco

# Chaves geradas pelo Sentry

SENTRY_DSN=http://usuario:senha@sentry.defensoria.to.def.br/id
SENTRY_TRACES_SAMPLE_RATE=1.0
```


## Criando virtualenv

```bash
mkvirtualenv solar -p python2
```

# Instalando UWSGI

[Tutorial: Como servir aplicativos do Django com uWSGI e Nginx no Debian 8](https://www.digitalocean.com/community/tutorials/how-to-serve-django-applications-with-uwsgi-and-nginx-on-debian-8)

```bash
sudo apt-get install libpcre3 libpcre3-dev

sudo -H pip install uwsgi
uwsgi --http :8000 --home diretorio_do_virtualenv --chdir diretorio_do_projeto -w config.wsgi
```

```bash
sudo mkdir -p /etc/uwsgi/sites
cd /etc/uwsgi/sites
sudo nano solar.ini
```

# Configurações UWSGI

```ini
[uwsgi]
project = solar
uid = desenvolvimento
gid = www-data

base = /home/%(uid)
project_root_dir = %(base)/%(project)
project_dir = %(project_root_dir)/%(project)

chdir = %(project_dir)/
home = %(base)/.virtualenvs/%(project)
module = config.wsgi:application

master = true
processes = 4
auto-procname = true
procname-prefix-spaced = %(project) -

# Finish off the configuration with the following lines
socket = /run/uwsgi/%(project).sock
chown-socket = %(uid):%(gid)
chmod-socket = 664
vacuum = true

# log
logfile-chown = true
# 10 megs, then rotate
log-maxsize = 10000000
logdir = %(project_root_dir)/log/uwsgi/
logto = %(logdir)/uwsgi-%n.log
log-backupname = %(logto).old

# Configuracoes extras em SOLAR-TO

#max-requests = 4000
#limit-as = 1024
#plugins = http,python
#listen = 4096
#logto = %(base)/log/uwsgi/uwsgi-%n.log
#log-maxsize = 1048576
#ignore-sigpipe=true
```

# Configurando serviço UWSGI

## Crie o arquivo uwsgi.service

```
sudo nano /etc/systemd/system/uwsgi.service
```

## Conteúdo do arquivo uwsgi.service

```ini
[Unit]
Description=uWSGI Emperor service

[Service]
ExecStartPre=/bin/bash -c 'mkdir -p /run/uwsgi; chown desenvolvimento:www-data /run/uwsgi'
ExecStart=/usr/local/bin/uwsgi --emperor /etc/uwsgi/sites
Restart=always
KillSignal=SIGQUIT
Type=notify
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```

## Habilite e inicialize o serviço do UWSGI

```
sudo systemctl enable uwsgi
sudo systemctl restart uwsgi
```

# Instalando e Configurando NGINX

```bash
sudo apt-get install nginx
```

## Crie o arquivo do site NGINX

```bash
sudo nano /etc/nginx/sites-available/solar
```

## Conteúdo do arquivo do site

```nginx
server {
    listen 80;
    server_name solar.defensoria.to.def.br;

    root /home/desenvolvimento/solar/src;

    error_log /home/desenvolvimento/solar/log/nginx/error.log;
    access_log /home/desenvolvimento/solar/log/nginx/access.log;

    location = /favicon.ico { access_log off; log_not_found off; }

    location / {
        include         uwsgi_params;
        uwsgi_pass      unix:/run/uwsgi/solar.sock;
    }

    location /media {
        alias /home/desenvolvimento/solar/src/media;
    }

    location /static {
        alias /home/desenvolvimento/solar/src/staticfiles_producao;
    }

}
```

## Crie o link simbólico no diretório de sites ativos

```bash
sudo ln -s /etc/nginx/sites-available/solar /etc/nginx/sites-enabled
```

## Valide a configuração do NGINX

```bash
sudo nginx -t
```

## Habilite e inicialize o serviço do NGINX

```bash
sudo systemctl enable nginx
sudo systemctl restart nginx
```
