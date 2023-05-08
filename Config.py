import pathlib
import json


class Config:

    _config_file = None
    _config_lookup = None

    @classmethod
    def _load_config(cls):
        if cls._config_file is None:
            cls._config_file = r'config\\config.json'

        path = pathlib.Path(cls._config_file)
        if not path.exists():
            raise ValueError('File: %s not found' % str(path.resolve()))
        with path.open() as f:
            cls._config_lookup = json.load(f)

    @classmethod
    def get(cls, key):
        if cls._config_lookup is None:
            cls._load_config()
        return cls._config_lookup[key]
