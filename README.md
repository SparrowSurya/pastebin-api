# Pastebin
A fastapi service for code sharing.

![tests](https://github.com/sparrowsurya/pastebin-api/actions/workflows/tests.yaml/badge.svg)
![os](https://img.shields.io/badge/os-Linux-blue)


## TODOS
* logger
* deployment


## Run
0. Download this project
```sh
git clone https://github.com/sparrowsurya/pastebin-api
```

1. Setup
```sh
virtualenv venv
source venv/bin/activate
```

Create a `.env` file with following values (fill the respective values of `DB_URL`)
```
ENV_NAME=development
BASE_URL=127.0.0.1:8000
DB_URL=postgresql://USERNAME:PASSWORD@HOSTNAME:PORT/DATABASE
INTERVAL=3600
```

2. Install dependencies
```sh
python3 -m pip install -r requirements.txt
```

3. Run the api
```sh
fastapi dev api/main.py
```
