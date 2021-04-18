import hashlib
from datetime import datetime

import simplejson as json
from flask import current_app
from sqlalchemy import desc

from webapp.account.models import Hash
from webapp.db import db


def md5_encode(data):
    """Возвращает md5-хэш для полученных данных."""
    data.pop('sentry', None)
    return hashlib.md5(json.dumps(data, sort_keys=True).encode('utf-8')).digest()


def check_hash(account_id, data, category):
    """Проверка хэша в БД.

    Функция получает идентификатор аккаунта, данные для проверки и категорию
    данных. Создает md5-хэш для полученных данных и сверяет их с хэшем в БД
    в зависимости от категории записи если в БД есть запись для данного
    аккаунта, иначе производится запись хэша и текущего времени. Если
    сравниваемый хэш отличается от записи в БД, то функция возвращает True,
    иначе False.
    """
    current_app.logger.info("Check hash function")
    db_hash = Hash.query.filter_by(account_id=account_id).order_by(desc(
        Hash.hash_id)).first()
    fresh_hash = md5_encode(data)
    if db_hash:
        if category == "account":
            if db_hash.account_hash != fresh_hash:
                db_hash.account_hash = fresh_hash
                db_hash.account_last_updated = datetime.utcnow()
                db.session.add(db_hash)
                db.session.commit()
                return True
        elif category == "inventory":
            if db_hash.inventory_hash != fresh_hash:
                db_hash.inventory_hash = fresh_hash
                db_hash.inventory_last_updated = datetime.utcnow()
                db.session.add(db_hash)
                db.session.commit()
                return True
        return False
    else:
        db_hash = Hash(
            account_hash=fresh_hash,
            inventory_hash=fresh_hash,
            account_last_updated=datetime.utcnow(),
            inventory_last_updated=datetime.utcnow(),
            account_id=account_id,
        )
        db.session.add(db_hash)
        db.session.commit()
        return True
