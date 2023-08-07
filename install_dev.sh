sudo apt-get update

sudo apt install python3.10-venv

git fetch --tags

git checkout master

pip install --upgrade pip

pip install --upgrade distlib

pip install --upgrade setuptools

python3 -m venv ENV

source ENV/bin/activate

pip install -r requirements/local.txt

pre-commit install
