import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
print(f"URL: {url}")
if url and (url.startswith("'") or url.startswith('"')):
    print("WARNING: URL has surrounding quotes!")
