import utils
from time import sleep
import random
import json
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException

TIMEOUT=10

# Get user information for a single user submission
def get_user_information(username, driver, headless=True, twitter_username=None, twitter_password=None):
    """ Get user information for a single user submission """
    if driver is None:
        print(f"Error: Driver is None for {username}")
        return None

    wait_time = 5  # Longer wait time for individual fetches
    try:
        print(f"Attempting to access profile for {username}")
        driver.get(f'https://twitter.com/{username}')
        sleep(random.uniform(1, wait_time))

        # Check if login is required
        login_required = is_login_required(driver, wait_time)
        if login_required:
            if twitter_username and twitter_password:
                login_to_twitter(driver, twitter_username, twitter_password)
                driver.get(f'https://twitter.com/{username}')
                sleep(random.uniform(1, wait_time))
            else:
                print(f"Login required for {username}, but credentials not provided.")
                return None

        user_data = scrape_user_data(driver, username)
        return {username: user_data}
    except Exception as e:
        print(f"An error occurred while fetching data for {username}: {str(e)}")
        return None

# Get user information for multiple users in bulk
def get_bulk_user_information(usernames, driver, headless=True, twitter_username=None, twitter_password=None):
    """ Get user information for multiple users in bulk """
    users_info = {}
    wait_time = 1  # Reduced wait time for bulk fetches

    for username in usernames:
        driver.get(f'https://twitter.com/{username}')
        try:
            WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="UserName"]')))
            user_data = scrape_user_data(driver, username)
            users_info[username] = user_data
            print(f"Scraped data for {username}")
        except Exception as e:
            print(f"Error scraping data for {username}: {str(e)}")
            continue

    return users_info

# Check if login is required for a user
def is_login_required(driver, wait_time):
    try:
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="UserName"]')))
        return False
    except:
        return True

# Login to Twitter
def login_to_twitter(driver, username, password):
    driver.get("https://twitter.com/i/flow/login")
    try:
        # Enter username
        username_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))
        username_input.send_keys(username)
        driver.find_element(By.XPATH, "//span[text()='Next']").click()

        # Handle phone/email verification if prompted
        try:
            verify_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@data-testid='ocfEnterTextTextInput']")))
            verify_input.send_keys("rscsfetcher@gmail.com")
            driver.find_element(By.XPATH, "//span[text()='Next']").click()
        except:
            pass  # If verification prompt doesn't appear, continue

        # Enter password
        password_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
        password_input.send_keys(password)
        driver.find_element(By.XPATH, "//span[text()='Log in']").click()

        # Handle unusual activity prompt
        try:
            email_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@name='text']")))
            email_input.send_keys("rscsfetcher@gmail.com")
            driver.find_element(By.XPATH, "//span[text()='Next']").click()
        except:
            pass  # If the unusual activity prompt doesn't appear, continue

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[@aria-label='Profile']")))
        print("Login successful")
    except Exception as e:
        print(f"Login failed: {str(e)}")
        driver.quit()
        raise

# Scrape user data from a single user submission
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
        except NoSuchElementException:
            user_data["description"] = "N/A"
            print(f"No description found for {user}")

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

# Log into the user's profile page
def log_user_page(user, driver, headless=True):
    sleep(random.uniform(1, 2))
    driver.get('https://twitter.com/' + user)
    sleep(random.uniform(1, 2))

# Get the followers of a user
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

# Get the following of a user
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

# Check if a string contains numbers
def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

# Find an element with multiple selectors
def find_element_with_multiple_selectors(driver, selectors):
    for selector in selectors:
        try:
            element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, selector)))
            return element
        except:
            continue
    return None

# Check if a user's profile is accessible
def is_profile_accessible(driver, wait_time):
    try:
        WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="UserName"]')))
        return True
    except:
        return False
