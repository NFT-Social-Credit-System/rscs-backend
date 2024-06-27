from . import utils
from time import sleep
import random
import json
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

TIMEOUT=10

def get_user_information(users, driver, headless=True, twitter_username=None, twitter_password=None):
    """ get user information if the "from_account" argument is specified """

    users_info = {}
    # user refers to the handle of the user to scrape
    for i, user in enumerate(users):
        driver.get(f'https://twitter.com/{user}')
        sleep(random.uniform(1, 2))

        # Check if login is required
        login_required = is_login_required(driver)
        if login_required:
            if twitter_username and twitter_password:
                login_to_twitter(driver, twitter_username, twitter_password)
                driver.get(f'https://twitter.com/{user}')
                sleep(random.uniform(1, 2))
            else:
                print(f"Login required for {user}, but credentials not provided.")
                continue

        if user is not None:
            user_data = scrape_user_data(driver, user)
            users_info[user] = user_data

    return users_info

def is_login_required(driver):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="UserName"]')))
        return False
    except:
        return True

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
        raise

def scrape_user_data(driver, user):
    user_data = {
        "username": user,
        "display_name": "N/A",
        "followers": "N/A",
        "pfp_url": "N/A",
        "banner_url": "N/A",
        "following": "N/A",
        "join_date": "N/A",
        "birth_date": "N/A",
        "location": "N/A",
        "website": "N/A",
        "description": "N/A"
    }

    try:
        # Display name
        try:
            displayname_element = driver.find_element(By.XPATH, '//div[@data-testid="UserName"]//span')
            displayname_html = displayname_element.get_attribute("innerHTML")
            soup = BeautifulSoup(displayname_html, "html.parser")
            user_data["display_name"] = ''.join([element if isinstance(element, str) else element.get('alt', '') if element.name == 'img' else element.get_text() for element in soup.contents])
        except Exception as e:
            print(f"Error fetching display name for {user}: {e}")

        # Following and Followers
        following_selectors = [
            "//a[contains(@href, '/following')]/span/span",
            "//div[@data-testid='UserProfileHeader_Items']//span[contains(text(), 'Following')]",
            "//div[@data-testid='primaryColumn']//span[contains(text(), 'Following')]/ancestor::a/span/span"
        ]
        followers_selectors = [
            "//a[contains(@href, '/followers')]/span/span",
            "//div[@data-testid='UserProfileHeader_Items']//span[contains(text(), 'Followers')]",
            "//div[@data-testid='primaryColumn']//span[contains(text(), 'Followers')]/ancestor::a/span/span"
        ]
        following_element = find_element_with_multiple_selectors(driver, following_selectors)
        user_data["following"] = following_element.text if following_element else "N/A"

        followers_element = find_element_with_multiple_selectors(driver, followers_selectors)
        user_data["followers"] = followers_element.text if followers_element else "N/A"

        # Profile Picture URL
        try:
            pfp_element = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//img[@alt="Opens profile photo"]'))
            )
            pfp_url = pfp_element.get_attribute("src")
            user_data["pfp_url"] = pfp_url.split('?')[0] if pfp_url else "N/A"
        except Exception as e:
            print(f"Error fetching profile picture for {user}: {e}")

        # Banner Picture URL
        try:
            banner_element = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@style,"background-image")]'))
            )
            banner_url = banner_element.value_of_css_property("background-image")
            user_data["banner_url"] = banner_url.split('url("')[1].split('")')[0] if 'url("' in banner_url else banner_url
        except Exception as e:
            print(f"Error fetching banner picture for {user}: {e}")

        # Description
        try:
            desc_element = driver.find_element(By.XPATH, '//div[contains(@data-testid,"UserDescription")]')
            user_data["description"] = desc_element.text
        except Exception as e:
            print(f"Error fetching description for {user}: {e}")

        # Website
        try:
            website_selectors = [
                "//a[@data-testid='UserUrl']",
                "//div[contains(@data-testid, 'UserProfileHeader_Items')]//a[contains(@href, 'http')]"
            ]
            website_element = find_element_with_multiple_selectors(driver, website_selectors)
            if website_element:
                user_data["website"] = website_element.get_attribute("href")
            else:
                # Fallback to looking for the website next to the location
                info_elements = driver.find_elements(By.XPATH, "//div[contains(@data-testid, 'UserProfileHeader_Items')]/span")
                for element in info_elements:
                    text = element.text
                    if "." in text or "com" in text or "org" in text or "net" in text:
                        user_data["website"] = text
                        break
        except Exception as e:
            print(f"Error fetching website for {user}: {e}")

        # Join Date, Location, and Birth Date
        info_selectors = [
            "//div[contains(@data-testid, 'UserProfileHeader_Items')]/span",
            "//div[contains(@data-testid, 'UserProfileHeader_Items')]//span"
        ]
        info_elements = driver.find_elements(By.XPATH, info_selectors[0]) or driver.find_elements(By.XPATH, info_selectors[1])
        
        for element in info_elements:
            text = element.text
            if "Joined" in text:
                user_data["join_date"] = text
            elif "Born" in text:
                user_data["birth_date"] = text
            elif not user_data["location"]:  # Only set location if it hasn't been set yet
                user_data["location"] = text

    except Exception as e:
        print(f"Error fetching user information for {user}: {e}")

    return user_data

def log_user_page(user, driver, headless=True):
    sleep(random.uniform(1, 2))
    driver.get('https://twitter.com/' + user)
    sleep(random.uniform(1, 2))

def get_users_followers(users, env, verbose=1, headless=True, wait=2, limit=float('inf'), file_path=None):
    followers = utils.get_users_follow(users, headless, env, "followers", verbose, wait=wait, limit=limit)

    if file_path == None:
        file_path = 'outputs/' + str(users[0]) + '_' + str(users[-1]) + '_' + 'followers.json'
    else:
        file_path = file_path + str(users[0]) + '_' + str(users[-1]) + '_' + 'followers.json'
    with open(file_path, 'w') as f:
        json.dump(followers, f)
        print(f"file saved in {file_path}")
    return followers

def get_users_following(users, env, verbose=1, headless=True, wait=2, limit=float('inf'), file_path=None):
    following = utils.get_users_follow(users, headless, env, "following", verbose, wait=wait, limit=limit)

    if file_path == None:
        file_path = 'outputs/' + str(users[0]) + '_' + str(users[-1]) + '_' + 'following.json'
    else:
        file_path = file_path + str(users[0]) + '_' + str(users[-1]) + '_' + 'following.json'
    with open(file_path, 'w') as f:
        json.dump(following, f)
        print(f"file saved in {file_path}")
    return following

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def find_element_with_multiple_selectors(driver, selectors):
    for selector in selectors:
        try:
            element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, selector)))
            return element
        except:
            continue
    return None
