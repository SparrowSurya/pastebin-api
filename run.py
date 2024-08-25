import uvicorn

from api.main import app


def main():
    log_config_file = "log_config.json"
    uvicorn.run(app, log_config=log_config_file)


if __name__ == "__main__":
    main()