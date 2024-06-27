from selenium import webdriver
from Scrape.user import get_user_information

def scrape_twitter_user(usernames : list[str]):
    # Scrape user profile data from list of usernames provided
    user_data = get_user_information(usernames)
    formatted_data = {}
    # Format the data to match the userData structure
    for user in user_data:
        formatted_data[user] = {
          "user": user_data[user],
          "display_name": user_data[user]['display_name'],
          "pfp_url": user_data[user]['pfp_url'],
          "followers": user_data[user]['followers'],
          "following": user_data[user]['following'],
          "website": user_data[user]['website'],
          "description": user_data[user]['description'],
        }
    return formatted_data

# Example usage
if __name__ == "__main__":
    username = ["@arb8020", "@roundtripgod", "@Nopointproven"]
    #username = ["@bonkleman_"]
    user_data = scrape_twitter_user(username)
    print(user_data)