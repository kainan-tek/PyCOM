import json
import os
from enum import Enum


class JsonFlag(Enum):
    SUCCESS = 0
    NO_FILE = 1
    ERR_OPEN_R = 2
    ERR_OPEN_W = 3
    EMPTY_DICT = 4


class JsonParser:
    def __init__(self, _file: str) -> None:
        self.file: str = _file

    def file_read(self, encode: str = "utf-8") -> tuple[JsonFlag, dict]:
        """
        Read a json file and return its content as a dictionary.
        """
        json_dict: dict = {}

        if not os.path.exists(self.file):
            return JsonFlag.NO_FILE, json_dict

        try:
            with open(self.file, mode="r", encoding=encode, newline="") as fp:
                json_dict = json.load(fp)
        except (OSError, IOError, json.JSONDecodeError):
            return JsonFlag.ERR_OPEN_R, json_dict

        if not json_dict:
            return JsonFlag.EMPTY_DICT, json_dict

        return JsonFlag.SUCCESS, json_dict

    def file_write(self, _json_dict: dict = None, encode: str = "utf-8") -> JsonFlag:
        """
        Write a dictionary to a json file.
        """
        if _json_dict is None:
            _json_dict = {}

        if not os.path.exists(self.file):
            return JsonFlag.NO_FILE

        try:
            with open(self.file, mode="w+", encoding=encode) as fp:
                json.dump(_json_dict, fp, indent=4, ensure_ascii=False)
        except (OSError, IOError):
            return JsonFlag.ERR_OPEN_W

        return JsonFlag.SUCCESS
