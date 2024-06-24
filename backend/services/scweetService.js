/**
 * Author: Ozzy (@meetg0d)
 * This file contains services for saving and scraping Twitter user data.
 */

const TwitterUser = require('../models/TwitterUserData');
const { spawn } = require('child_process');

/**
 * Saves or updates a Twitter user's data in the database.
 * @param {Object} userData - The user data to save.
 * @returns {Promise<Object>} The saved user object.
 */

const saveTwitterUser = async (userData) => {
  try {
    const { username, displayName, profilePictureUrl, followersCount } = userData;
    
    const user = await TwitterUser.findOneAndUpdate(
      { username },
      { username, displayName, profilePictureUrl, followersCount },
      { upsert: true, new: true }
    );

    return user;
  } catch (error) {
    console.error('Error saving Twitter user:', error);
    throw error;
  }
};

/**
 * Placeholder function for future Twitter user data scraping implementation.
 * @param {string} username - The username to scrape data for.
 * @returns {Promise<Object>} An empty object (placeholder).
 */
const scrapeTwitterUser = (username) => {
  // Placeholder for future scraping logic
  console.log(`Scraping for user ${username} is not implemented yet.`);
  return Promise.resolve({});
};

module.exports = { saveTwitterUser, scrapeTwitterUser };
