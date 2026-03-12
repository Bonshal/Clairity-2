
import os
import sys
import logging
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_genai_v2")

# Try importing V2
try:
    from google import genai
    logger.info(f"Successfully imported google.genai")
except ImportError as e:
    logger.error(f"Failed to import google.genai: {e}")
    sys.exit(1)

# Load Key
from dotenv import load_dotenv
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_file = os.path.join(project_root, ".env")
load_dotenv(env_file)

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.error("No API key found")
    sys.exit(1)

logger.info(f"Using API Key: {api_key[:4]}...")

async def test_model(model_name):
    logger.info(f"Testing model: {model_name}...")
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents="Say 'Hello World'",
        )
        logger.info(f"SUCCESS with {model_name}: {response.text}")
        return True
    except Exception as e:
        logger.error(f"FAILED with {model_name}: {e}")
        return False

async def main():
    logger.info("Listing available models...")
    try:
        client = genai.Client(api_key=api_key)
        for model in client.models.list():
            logger.info(f"Available Model: {model.name}")
    except Exception as e:
        logger.error(f"Failed to list models: {e}")

    models = [
        "gemini-2.5-flash", 
        "gemini-1.5-flash"
    ]
    
    for m in models:
        await test_model(m)

if __name__ == "__main__":
    asyncio.run(main())
