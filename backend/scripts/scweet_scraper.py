import os
from dotenv import load_dotenv
from selenium import webdriver
from Scrape.user import get_user_information
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

load_dotenv()  # This loads the variables from .env

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

def scrape_twitter_user(usernames: list[str], twitter_username, twitter_password):
    driver = webdriver.Chrome()
    user_data = {}
    for username in usernames:
        driver.get(f"https://twitter.com/{username}")
        try:
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="UserName"]')))
        except:
            print(f"Login required for {username}")
            login_to_twitter(driver, twitter_username, twitter_password)
            driver.get(f"https://twitter.com/{username}")
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="UserName"]')))
        
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="UserName"]')))
            user_info = get_user_information([username], driver)
            if user_info:
                user_data.update(user_info)
            else:
                print(f"Failed to fetch data for {username}")
        except Exception as e:
            print(f"Error loading data for {username}: {str(e)}")

    formatted_data = {}
    for user in user_data:
        formatted_data[user] = {
            "user": user_data[user],
            "display_name": user_data[user].get('display_name', 'N/A'),
            "pfp_url": user_data[user].get('pfp_url', 'N/A'),
            "followers": user_data[user].get('followers', 'N/A'),
            "following": user_data[user].get('following', 'N/A'),
            "website": user_data[user].get('website', 'N/A'),
            "description": user_data[user].get('description', 'N/A'),
            "location": user_data[user].get('location', 'N/A'),
            "join_date": user_data[user].get('join_date', 'N/A'),
            "birth_date": user_data[user].get('birth_date', 'N/A'),
        }
    driver.quit()
    return formatted_data

# Example usage
if __name__ == "__main__":
    username = ["@arb8020", "@roundtripgod", "@Nopointproven", "@itsGboii"]
    twitter_username = os.getenv('TWITTER_USERNAME')
    twitter_password = os.getenv('TWITTER_PASSWORD')
    user_data = scrape_twitter_user(username, twitter_username, twitter_password)
    print(user_data)