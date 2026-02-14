
import os
from apify_client import ApifyClient
from dotenv import load_dotenv
import json

def main():
    load_dotenv()
    client = ApifyClient(token=os.environ["APIFY_TOKEN"])
    actor = client.actor("comchat/reddit-api-scraper").get()
    print(json.dumps(actor, indent=2, default=str))

if __name__ == "__main__":
    main()
