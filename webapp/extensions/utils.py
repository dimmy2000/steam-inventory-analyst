"""Дополнительные утилиты."""
import hashlib

import simplejson as json


def md5_encode(data):
    """Возвращает md5-хэш для полученных данных."""
    data.pop('sentry', None)
    return hashlib.md5(
        json.dumps(data, sort_keys=True).encode('utf-8'),
    ).digest()
