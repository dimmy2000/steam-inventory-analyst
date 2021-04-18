"""Test app run."""
import webapp
from webapp import factory


if __name__ == "__main__":
    app = factory.create_app(celery=webapp.celery)
    app.run()
