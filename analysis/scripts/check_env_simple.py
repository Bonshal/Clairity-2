
import sys
import os
# mimic uvicorn execution from inside 'analysis' folder
sys.path.append(os.getcwd()) 

try:
    from src.config import settings
    # secure print
    db = settings.database_url
    mongo = settings.mongodb_uri
    print(f"DB URL: {db[:15]}... (len={len(db)})")
    print(f"Mongo URI: {mongo[:15]}... (len={len(mongo)})")
except Exception as e:
    print(f"Error loading settings: {e}")
