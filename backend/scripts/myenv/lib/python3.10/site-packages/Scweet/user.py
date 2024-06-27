from . import utils
from time import sleep
import random
import json
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
                following = driver.find_element(By.XPATH, '//a[contains(@href,"/following")]/span[1]/span[1]').text
        
                # Changed from followers to verified_followers 
                followers =  driver.find_element(By.XPATH, '//a[contains(@href,"/verified_followers")]/span[1]/span[1]').text
               
            except Exception as e:
                print(f"Error fetching following/followers for {user}: {e}")
                continue

            # Website
            try:
                element = driver.find_element(By.XPATH, '//div[contains(@data-testid,"UserProfileHeader_Items")]//a')
                website = element.get_attribute("href")
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

            # Join Date, Birthday, and Location
            try:
                join_date = driver.find_element(By.XPATH, '//div[contains(@data-testid,"UserProfileHeader_Items")]/span[3]').text
                birthday = driver.find_element(By.XPATH, '//div[contains(@data-testid,"UserProfileHeader_Items")]/span[2]').text
                location = driver.find_element(By.XPATH, '//div[contains(@data-testid,"UserProfileHeader_Items")]/span[1]').text
            except Exception as e:
                print(f"Error fetching join date/birthday/location for {user}: {e}")
                try:
                    join_date = driver.find_element(By.XPATH, '//div[contains(@data-testid,"UserProfileHeader_Items")]/span[2]').text
                    span1 = driver.find_element(By.XPATH, '//div[contains(@data-testid,"UserProfileHeader_Items")]/span[1]').text
                    if hasNumbers(span1):
                        birthday = span1
                        location = ""
                    else:
                        location = span1
                        birthday = ""
                except Exception as e:
                    print(f"Error fetching join date/birthday/location (second attempt) for {user}: {e}")
                    try:
                        join_date = driver.find_element(By.XPATH, '//div[contains(@data-testid,"UserProfileHeader_Items")]/span[1]').text
                        birthday = ""
                        location = ""
                    except Exception as e:
                        print(f"Error fetching join date/birthday/location (third attempt) for {user}: {e}")
                        join_date = ""
                        birthday = ""
                        location = ""

            print("--------------- " + user + " information : ---------------")
            print("Handle: ", user)
            print("Banner picture: ", banner_url)
            print("Profile picture: ", pfp_url)
            print("Display name : ", displayname)
            print("Following : ", following)
            print("Followers : ", followers)
            print("Location : ", location)
            print("Join date : ", join_date)
            print("Birth date : ", birthday)
            print("Description : ", desc)
            print("Website : ", website)
            users_info[user] = {
                "display_name" : displayname,
                "banner_url" : banner_url,
                "pfp_url" : pfp_url,
                "following": following,
                "followers": followers,
                "join_date": join_date,
                "birthday": birthday,
                "location": location,
                "website": website,
                "description": desc
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