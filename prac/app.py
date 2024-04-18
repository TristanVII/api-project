import time
import connexion
import requests
import datetime
import json
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from connexion import FlaskApp, NoContent
from load_configs import load_app_conf, load_log_conf

LOGGER = load_log_conf()
CONFIG = load_app_conf()


def mock_get(idx):
    return {"response": int(idx)}, 201


def mock_post(body):
    LOGGER.info(f"Received {body}")
    return NoContent, 201


app = FlaskApp(__name__, specification_dir='')

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_api("./openapi.yaml", strict_validation=True,
            validate_responses=True, base_path="/mock")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8999)
