"""Логика создания и изменения базы данных."""
from webapp import app, db

if __name__ == "__main__":
    db.create_all(app=app)