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

def get_user_information(users, driver=None, headless=True):
    """ get user information if the "from_account" argument is specified """

    driver = utils.init_driver(headless=headless)

    users_info = {}
    # user refers to the handle of the user to scrape
    for i, user in enumerate(users):

        log_user_page(user, driver)

        if user is not None:

            # Following and Followers
            try:
                follow_selectors = [
                    "//a[contains(@href, '/following')]/span/span",
                    "//a[contains(@href, '/followers')]/span/span",
                    "//div[@data-testid='UserProfileHeader_Items']//span[contains(text(), 'Following') or contains(text(), 'Followers')]"
                ]
                following_element = find_element_with_multiple_selectors(driver, follow_selectors)
                following = following_element.text
        
                followers_element = find_element_with_multiple_selectors(driver, follow_selectors)
                followers = followers_element.text
               
            except Exception as e:
                print(f"Error fetching following/followers for {user}: {e}")
                continue

            # Website
            try:
                website_selectors = [
                    "//a[contains(@href, 'http') and @rel='noopener noreferrer nofollow']",
                    "//div[contains(@data-testid, 'UserProfileHeader_Items')]//a[contains(@href, 'http')]",
                    "//div[contains(@data-testid, 'UserProfileHeader_Items')]//span[contains(text(), '.com') or contains(text(), '.org') or contains(text(), '.net')]"
                ]
                website_element = find_element_with_multiple_selectors(driver, website_selectors)
                if website_element:
                    website = website_element.get_attribute("href")
                else:
                    website = ""
            except Exception as e:
                print(f"Error fetching website for {user}: {e}")
                website = ""

            # User Description
            try:
                desc = driver.find_element(By.XPATH, '//div[contains(@data-testid,"UserDescription")]').text
            except Exception as e:
                print(f"Error fetching description for {user}: {e}")
                desc = ""

            # Display name (which Twitter calls the username on their site i.e. different from a person's @handle)
            """
            try:
                displayname = driver.find_element(By.XPATH, '//div[@data-testid="UserName"]//span').text
            except Exception as e:
                print(f"Error fetching username for {user}: {e}")
                displayname = ""
            """
            try:
                displayname_element = driver.find_element(By.XPATH, '//div[@data-testid="UserName"]//span')
                displayname_html = displayname_element.get_attribute("innerHTML")
                soup = BeautifulSoup(displayname_html, "html.parser")
                displayname = ''.join([element if isinstance(element, str) else element.get('alt', '') if element.name == 'img' else element.get_text() for element in soup.contents])
            except Exception as e:
                print(f"Error fetching username for {user}: {e}")
                displayname = ""


            # Banner Picture URL
            try:
                banner_element = WebDriverWait(driver, TIMEOUT).until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@style,"background-image")]'))
                )
                banner_url = banner_element.value_of_css_property("background-image").split('"')[1]
            except Exception as e:
                print(f"Error fetching profile picture for {user}: {e}")
                banner_url = ""

            # Profile Picture URL
            try:
                pfp_element = WebDriverWait(driver, TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, '//img[@alt="Opens profile photo"]'))
                    )
                pfp_url = pfp_element.get_attribute("src")
            except Exception as e:
                print(f"Error fetching profile picture for {user}: {e}")
                pfp_url = ""

            # Join Date, Location, and Birth Date
            try:
                info_selectors = [
                    "//div[contains(@data-testid, 'UserProfileHeader_Items')]/span",
                    "//div[contains(@data-testid, 'UserProfileHeader_Items')]//span"
                ]
                info_elements = driver.find_elements(By.XPATH, info_selectors[0]) or driver.find_elements(By.XPATH, info_selectors[1])
                
                join_date = "N/A"
                location = "N/A"
                birth_date = "N/A"

                for element in info_elements:
                    text = element.text
                    if "Joined" in text:
                        join_date = text
                    elif "Born" in text:
                        birth_date = text
                    elif not any(char.isdigit() for char in text):
                        location = text

            except Exception as e:
                print(f"Error fetching user information for {user}: {e}")
                join_date = "N/A"
                location = "N/A"
                birth_date = "N/A"

            print("--------------- " + user + " information : ---------------")
            print("Handle: ", user)
            print("Banner picture: ", banner_url or "N/A")
            print("Profile picture: ", pfp_url or "N/A")
            print("Display name : ", displayname or "N/A")
            print("Following : ", following or "N/A")
            print("Followers : ", followers or "N/A")
            print("Location : ", location)
            print("Join date : ", join_date)
            print("Birth date : ", birth_date)
            print("Description : ", desc or "N/A")
            print("Website : ", website or "N/A")
            users_info[user] = {
                "display_name" : displayname or "N/A",
                "banner_url" : banner_url or "N/A",
                "pfp_url" : pfp_url or "N/A",
                "following": following or "N/A",
                "followers": followers or "N/A",
                "join_date": join_date,
                "birth_date": birth_date,
                "location": location,
                "website": website or "N/A",
                "description": desc or "N/A"
            }

    driver.close()
    return users_info

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