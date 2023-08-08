git fetch --tags


pip install --upgrade pip

pip install --upgrade distlib

pip install --upgrade setuptools

python -m venv ENV

ENV\Scripts\activate

pip install -r requirements/local.txt

pre-commit install
