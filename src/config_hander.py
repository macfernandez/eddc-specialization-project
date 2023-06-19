from src.utils import load_json


class ConfigHandler():

    def __init__(self, config_path: str):
        self.config = load_json(config_path)

    def get(self, key: str):
        return self.config.get(key)