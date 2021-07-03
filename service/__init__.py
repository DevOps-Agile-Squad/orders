"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database

Source: https://github.com/nyu-devops/project-template/blob/master/service/__init__.py
"""
import os
import sys
import logging
from flask import Flask


# Create Flask application
app = Flask(__name__)
app.config.from_object("config")

# Import the rutes After the Flask app is created
from service import routes

# Set up logging for production
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.propagate = False
    # Make all log formats consistent
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s", "%Y-%m-%d %H:%M:%S %z"
    )
    for handler in app.logger.handlers:
        handler.setFormatter(formatter)
    app.logger.info("Logging handler established")

app.logger.info(70 * "*")
app.logger.info("  M Y   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")
routes.init_db()  # make our sqlalchemy tables



app.logger.info("Service inititalized!")