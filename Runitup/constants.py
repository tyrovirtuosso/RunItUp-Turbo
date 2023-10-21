import yaml

with open("Runitup/runitup_config.yaml", "r") as yaml_file:
    config = yaml.safe_load(yaml_file)

DEVELOPMENT_MODE = config["system"]["development"] is True

DB_PARAMS = {
    "type": config["db"]["type"],
    "host": config["db"]["host"],
    "port": config["db"]["port"],
    "user": config["db"]["user"],
    "password": config["db"]["password"],
    "database": config["db"]["database"],
}
