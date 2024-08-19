# Pastebin
A fastapi service for code sharing.


## TODOS
* deploy to vercel
* a cronjob for autoatically deleting the expired pastes
* logger


## Run
0. Download this project
```sh
git clone https://github.com/sparrowsurya/pastebin-api.git
```

1. Setup
```sh
virtualenv venv
source venv/bin/activate
```

Create a `.env` file with following values
```
ENV_NAME=development
BASE_URL=127.0.0.1:8000
DB_URL=sqlite:///./db.sqlite3
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
