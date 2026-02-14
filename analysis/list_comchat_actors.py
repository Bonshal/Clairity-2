
import os
from apify_client import ApifyClient
from dotenv import load_dotenv

def main():
    load_dotenv()
    client = ApifyClient(token=os.environ["APIFY_TOKEN"])
    # This might find actors by comchat
    actors = client.actors().list()
    for actor in actors.items:
        if actor.get("username") == "comchat" or "comchat" in actor.get("name", "").lower():
            print(f"Name: {actor.get('name')}, ID: {actor.get('id')}, Username: {actor.get('username')}")

if __name__ == "__main__":
    main()
