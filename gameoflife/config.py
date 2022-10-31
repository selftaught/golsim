import json
import os

from benedict import benedict


class Config:
    def __init__(self, file : str = 'config.json') -> None:
        self.cfg = benedict({})
        self.file = file
        self.load()

    def dir(self) -> str:
        path = os.path.dirname(os.path.realpath(__file__))
        return os.path.abspath(f"{path}/../")

    def path(self) -> str:
        root = self.dir()
        return os.path.abspath(f"{root}/{self.file}")

    def load(self) -> None:
        self.cfg = benedict(self.path(), format='json')

    def get(self, key, default=None):
        if key in self.cfg:
            return self.cfg[key]
        elif default is not None:
            return default
        raise KeyError(f"Couldn't find key '{key}' in config")