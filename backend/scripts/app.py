from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from dotenv import load_dotenv
from threading import Thread, Lock
from queue import PriorityQueue
import os
import logging
import time
from user import login_to_twitter, get_user_information

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Connect to MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')
client = MongoClient(MONGODB_URI)
db = client.RSCS
users_collection = db.Users
is_scraping = False
scrape_lock = Lock()
driver = None
username_queue = PriorityQueue()
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')

# Create a Chrome driver
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.binary_location = '/usr/bin/chromium-browser'
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        logging.error(f"Error creating driver: {str(e)}")
        raise

# Initialize the driver and log in to Twitter
def initialize_driver():
    global driver
    driver = create_driver()
    login_to_twitter(driver, TWITTER_USERNAME, TWITTER_PASSWORD)
    driver.get("https://twitter.com/home")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="primaryColumn"]'))
    )
    logging.info("Driver logged in and navigated to home successfully.")

# Scrape process
def scrape_process():
    global is_scraping, driver
    is_scraping = True
    logging.info("Starting scrape process")
    try:
        while not username_queue.empty():
            priority, username = username_queue.get()
            logging.info(f"Processing user: {username}")
            try:
                logging.info(f"Scraping {username}")
                driver.get(f'https://twitter.com/{username}')
                user_data = get_user_information(username, driver)
                if user_data and username in user_data:
                    update_user_in_database(user_data[username])
                    logging.info(f"Successfully scraped and updated data for {username}")
                    print(f"Highlight: User {username} successfully scraped and saved to database")
                else:
                    logging.warning(f"Failed to scrape data for {username}")
            except Exception as e:
                logging.error(f"Error scraping {username}: {str(e)}")
            finally:
                username_queue.task_done()
                driver.get("https://twitter.com/home")
            logging.info(f"Remaining users in queue: {username_queue.qsize()}")
    except Exception as e:
        logging.error(f"An error occurred during scraping: {str(e)}")
    finally:
        is_scraping = False
        logging.info("Scrape process completed")

# Start the scrape process
def start_scrape_process():
    global scrape_thread
    if not is_scraping:
        scrape_thread = Thread(target=scrape_process)
        scrape_thread.start()

# Scrape a single user
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    username = data.get('username')
    
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    username = username.lower()  # Convert to lowercase
    
    # Check if user already exists in the database
    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        return jsonify({'message': f'User {username} already exists in the database'}), 200

    username_queue.put((1, username))  # Priority 1 for individual scrape requests
    start_scrape_process()

    return jsonify({'message': f'Added {username} to scrape queue'}), 202

# Scrape all users
@app.route('/scrape-all', methods=['POST'])
def scrape_all():
    all_users = list(users_collection.find({}, {'username': 1, '_id': 0}))
    
    for user in all_users:
        username = user['username'].lower()
        username_queue.put((2, username))  # Priority 2 for scrape-all requests
    
    start_scrape_process()
    
    return jsonify({
        'success': True,
        'message': f'Added {len(all_users)} users to scrape queue'
    })

# Get the status of the scrape process
@app.route('/scrape-status', methods=['GET'])
def scrape_status():
    return jsonify({
        'is_scraping': is_scraping,
        'queue_size': username_queue.qsize()
    })

# Get the status of the scrape process for all users
@app.route('/scrape-all-status', methods=['GET'])
def scrape_all_status():
    return jsonify({
        'is_scraping_all': is_scraping,
        'queue_size': username_queue.qsize()
    })

# Update a user in the database 
def update_user_in_database(user_data):
    logging.info(f"Updating database for user: {user_data['username']}")
    users_collection.update_one(
        {'username': user_data['username'].lower()},
        {'$set': user_data},
        upsert=True
    )
    logging.info(f"Database updated for user: {user_data['username']}")

# Run the Flask app
if __name__ == '__main__':
    try:
        initialize_driver()
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logging.error(f"Failed to initialize driver: {str(e)}")
        logging.error("Exiting application.")
        if driver:
            driver.quit()
