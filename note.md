## set up virtual environment


```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12
# ダウンロードと実行を一度に行う
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
python3.12 -m pip install pipenv
# Pipfileを作成
pipenv --python 3.12
# 必要に応じて
pipenv lock -r > requirements.txt

```

precommit の hook の設定

```bash
pipenv run pre-commit install
```
