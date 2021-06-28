"""
Global Configuration for Application

Source: https://github.com/nyu-devops/project-template/blob/master/config.py
"""
import os

# Get configuration from environment
DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///../development.db")

# Configure SQLAlchemy
SQLALCHEMY_DATABASE_URI = DATABASE_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Secret for session management
SECRET_KEY = os.getenv("SECRET_KEY", "s3cr3t-key-shhhh")