""" Config file for the application 
This file contains the configuration for the application."""

__author__ = "Akele Benjamin(620130803)"
import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 