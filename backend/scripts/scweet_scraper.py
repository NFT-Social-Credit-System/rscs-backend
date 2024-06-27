import os
from dotenv import load_dotenv
from selenium import webdriver
from Scrape.user import get_user_information
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import pickle

load_dotenv()  # This loads the variables from .env

TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')

def connect_to_mongodb():
    client = MongoClient(os.getenv('MONGODB_URI'))
    return client.RSCS

def update_user_in_database(user_data):
    db = connect_to_mongodb()
    users_collection = db.Users
    result = users_collection.update_one(
        {'username': user_data['username']},
        {'$set': user_data},
        upsert=True
    )
    print(f"Database update result: {result.raw_result}")

def login_to_twitter(driver, username, password):
    driver.get("https://twitter.com/i/flow/login")
    try:
        username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))
        username_input.send_keys(username)
        driver.find_element(By.XPATH, "//span[text()='Next']").click()

        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(password)
        driver.find_element(By.XPATH, "//span[text()='Log in']").click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Profile']")))
        print("Login successful")
    except Exception as e:
        print(f"Login failed: {str(e)}")
        driver.quit()
        raise

def scrape_twitter_user(usernames: list[str]):
    driver = webdriver.Chrome()
    user_data = {}
    
    # Check if cookies exist and load them
    if os.path.exists('twitter_cookies.pkl'):
        cookies = pickle.load(open("twitter_cookies.pkl", "rb"))
        driver.get("https://twitter.com")
        for cookie in cookies:
            driver.add_cookie(cookie)
    else:
        # Log in and save cookies
        login_to_twitter(driver, TWITTER_USERNAME, TWITTER_PASSWORD)
        pickle.dump(driver.get_cookies(), open("twitter_cookies.pkl", "wb"))

    for username in usernames:
        driver.get(f"https://twitter.com/{username}")
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="UserName"]')))
            user_info = get_user_information([username], driver, headless=False, twitter_username=TWITTER_USERNAME, twitter_password=TWITTER_PASSWORD)
            if user_info and username in user_info:
                user_data[username] = user_info[username]
                update_user_in_database(user_info[username])
                print(f"Scraping completed and entry updated for \"{username}\"")
            else:
                print(f"Failed to fetch data for {username}")
        except Exception as e:
            print(f"Error loading data for {username}: {str(e)}")

    driver.quit()
    return user_data

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) < 2:
        print("Usage: python scweet_scraper.py <username>")
        sys.exit(1)
    username = [sys.argv[1]]
    user_data = scrape_twitter_user(username)
    print("Scraped user data:")
    print(json.dumps(user_data, indent=2))
