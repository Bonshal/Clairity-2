
import os
from apify_client import ApifyClient
from dotenv import load_dotenv

def main():
    load_dotenv()
    client = ApifyClient(token=os.environ["APIFY_TOKEN"])
    try:
        actor = client.actor("comchat/reddit-scraper").get()
        print(f"Found actor comchat/reddit-scraper: {actor['id']}")
    except Exception as e:
        print(f"comchat/reddit-scraper not found: {e}")

if __name__ == "__main__":
    main()
