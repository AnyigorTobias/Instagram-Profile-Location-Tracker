"""This module extracts information from your `.env` file so that
you can use your Social Scrapy Keys in other parts of the application.
"""

# The os library allows you to communicate with a computer's
# operating system: https://docs.python.org/3/library/os.html
import os

# pydantic used for data validation: https://pydantic-docs.helpmanual.io/
from pydantic_settings import BaseSettings


def return_full_path(filename: str = ".env") -> str:
    """Uses os to return the correct path of the `.env` file."""
    absolute_path = os.path.abspath(__file__)
    directory_name = os.path.dirname(absolute_path)
    full_path = os.path.join(directory_name, filename)
    return full_path


class Settings(BaseSettings):
    """Uses pydantic to define settings for project."""

    CONSUMER_KEY: str
    CONSUMER_SECRET: str
    
    

    class Config:
        env_file = return_full_path(".env")


# Create instance of `Settings` class that will be imported
# in lesson notebooks and the other modules for application.
settings = Settings()
