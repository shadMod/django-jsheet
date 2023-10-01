import json

from django.conf import settings


def get_type_header(field: str) -> str:
    with open(settings.BASE_PATH_LIBS + "/assets/constats.json") as fn:
        data = json.loads(fn.read())[field]

    res = json.dumps(data)
    for key in data:
        clean_key = key.replace('"', "")
        res = res.replace(f'"{key}"', clean_key)
    return res


def column_header(field: str, value: str, source: list = None) -> str:
    if source is None:
        clm = get_type_header(field) % value
    else:
        clm = get_type_header(field) % (value, source)
    clm = "".join(clm.split()).replace('"', "'")
    return clm


def get_fetch_js() -> str:
    with open(settings.BASE_PATH_LIBS + "/assets/fetch_js.js") as fn:
        val = fn.read()

    return val
