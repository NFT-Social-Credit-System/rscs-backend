import os
from dotenv import load_dotenv
from selenium import webdriver
from Scrape.user import get_user_information, get_bulk_user_information
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import pickle
from datetime import datetime, timedelta
from pymongo.operations import UpdateOne
from Scrape.user import get_user_information, get_bulk_user_information
from time import sleep
import random
from bs4 import BeautifulSoup

load_dotenv()  # This loads the variables from .env

TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')

# Establish connection to MongoDB
def connect_to_mongodb():
    client = MongoClient(os.getenv('MONGODB_URI'))
    return client.RSCS

# Update or insert user data in the database
def update_user_in_database(user_data):
    db = connect_to_mongodb()
    users_collection = db.Users
    result = users_collection.update_one(
        {'username': user_data['username']},
        {'$set': user_data},
        upsert=True
    )
    print(f"Database update result: {result.raw_result}")

# Perform Twitter login using Selenium
def login_to_twitter(driver, username, password):
    driver.get("https://twitter.com/i/flow/login")
    try:
        username_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "text")))
        username_input.send_keys(username)
        driver.find_element(By.XPATH, "//span[text()='Next']").click()

        password_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(password)
        driver.find_element(By.XPATH, "//span[text()='Log in']").click()

        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Profile']")))
        print("Login successful")
    except Exception as e:
        print(f"Login failed: {str(e)}")
        driver.quit()
        raise

# Check if a Twitter profile is accessible
def is_profile_accessible(driver):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="UserName"]')))
        return True
    except:
        return False
    

# Save browser cookies to a file
def save_cookies(driver):
    cookies = driver.get_cookies()
    for cookie in cookies:
        if 'expiry' in cookie:
            cookie['expiry'] = int(cookie['expiry'])
        else:
            cookie['expiry'] = int((datetime.now() + timedelta(days=30)).timestamp())
    pickle.dump(cookies, open("twitter_cookies.pkl", "wb"))

# Load cookies from file and add them to the browser
def load_cookies(driver):
    if os.path.exists('twitter_cookies.pkl'):
        cookies = pickle.load(open("twitter_cookies.pkl", "rb"))
        current_time = datetime.now().timestamp()
        
        if all(cookie.get('expiry', 0) > current_time for cookie in cookies):
            driver.get("https://twitter.com")
            for cookie in cookies:
                driver.add_cookie(cookie)
            driver.refresh()
            return True
    return False

# Scrape Twitter user data for a list of usernames
def scrape_twitter_user(usernames: list[str]):
    driver = webdriver.Chrome()
    user_data = {}
    
    try:
        if not load_cookies(driver):
            print("No valid cookies found. Logging in...")
            login_to_twitter(driver, TWITTER_USERNAME, TWITTER_PASSWORD)
            save_cookies(driver)
        
        for username in usernames:
            print(f"Attempting to access {username}'s profile...")
            driver.get(f'https://twitter.com/{username}')
            sleep(random.uniform(1, 3))  # Add a small delay

            if is_profile_accessible(driver):
                user_info = get_user_information(username, driver)
                if user_info and username in user_info:
                    user_data[username] = user_info[username]
                    update_user_in_database(user_info[username])
                    print(f"Scraping completed and entry updated for \"{username}\"")
                else:
                    print(f"Failed to fetch data for {username}")
            else:
                print(f"Profile not accessible for {username}")

    except Exception as e:
        print(f"An error occurred during scraping: {str(e)}")
    finally:
        driver.quit()
    return user_data

# Scrape Twitter user data for all users in the database
def scrape_all_users(usernames: list[str], driver):
    user_data = {}
    
    try:
        for username in usernames:
            print(f"Attempting to access {username}'s profile...")
            driver.get(f'https://twitter.com/{username}')
            sleep(random.uniform(1, 3))  # Add a small delay

            if is_profile_accessible(driver):
                user_info = get_user_information(username, driver)
                if user_info and username in user_info:
                    user_data[username] = user_info[username]
                    print(f"Successfully scraped data for {username}")
                else:
                    print(f"Failed to fetch data for {username}")
            else:
                print(f"Profile not accessible for {username}")

        if user_data:
            print("Updating database with scraped data...")
            db = connect_to_mongodb()
            users_collection = db.Users
            bulk_operations = [
                UpdateOne({'username': username}, {'$set': data}, upsert=True)
                for username, data in user_data.items()
            ]
            result = users_collection.bulk_write(bulk_operations)
            print(f"Database update result: {result.bulk_api_result}")

    except Exception as e:
        print(f"An error occurred during bulk scraping: {str(e)}")
    
    return user_data

# Main function to run the script
if __name__ == "__main__":
    import sys
    import json
    from pymongo import MongoClient

    # Connect to the database and fetch all usernames
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client.RSCS
    users_collection = db.Users
    all_users = list(users_collection.find({}, {'username': 1, '_id': 0}))
    all_usernames = [user['username'] for user in all_users]

    print(f"Found {len(all_usernames)} users in the database.")
    print("Usernames:", all_usernames)

    # Call scrape_all_users with all usernames from the database
    user_data = scrape_all_users(all_usernames, driver)

    print("Scraped user data:")
    print(json.dumps(user_data, indent=2))

    print(f"Successfully updated {len(user_data)} users.")