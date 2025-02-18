import os
from dotenv import load_dotenv

# Load environment variables from the root .env
load_dotenv()

# Set the environment (default, if not defined, uses the root .env)
ENV = os.getenv("ENVIRONMENT", "local")  # "local" is just a reference
load_dotenv(f"config/{ENV}.env", override=True)  # If it exists, load it

DEBUG = os.getenv("DEBUG", "False") == "True"

RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"

if RUNNING_IN_DOCKER:
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
else:
    ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_LOCAL_URL", "http://localhost:9200")

INDEX_NAME = os.getenv("INDEX_NAME", "default_index")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")