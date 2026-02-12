"""Setup configuration"""
from setuptools import setup, find_packages

setup(
    name="analytics-api",
    version="1.0.0",
    description="Event-Driven Analytics & Audit API",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "sqlalchemy==2.0.23",
        "psycopg2-binary==2.9.9",
        "pydantic==2.5.0",
        "redis==5.0.1",
        "celery==5.3.4",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-cov==4.1.1",
            "black==23.12.0",
            "flake8==6.1.0",
            "mypy==1.7.1",
        ],
    },
)
