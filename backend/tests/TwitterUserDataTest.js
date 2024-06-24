/**
 * Author: Ozzy (@meetg0d)
 * This file contains test data and a function to save it to MongoDB.
 */

const path = require('path');
const dotenv = require('dotenv');

// Load environment variables
const envPath = path.resolve(__dirname, '../../.env');
console.log('Attempting to load .env from:', envPath);
const result = dotenv.config({ path: envPath });

if (result.error) {
  console.error('Error loading .env file:', result.error);
} else {
  console.log('.env file loaded successfully');
}

const mongoose = require('mongoose');
const { saveTwitterUser } = require('../services/scweetService');

// Test user data
const testUsers = [
  {
    username: "testuser1",
    displayName: "Test User 1",
    profilePictureUrl: "https://example.com/pic1.jpg",
    followersCount: 1000
  },
  {
    username: "testuser2",
    displayName: "Test User 2",
    profilePictureUrl: "https://example.com/pic2.jpg",
    followersCount: 2000
  },
  {
    username: "testuser3",
    displayName: "Test User 3",
    profilePictureUrl: "https://example.com/pic3.jpg",
    followersCount: 3000
  }
];

/**
 * Saves test user data to MongoDB.
 */
async function saveTestData() {
  try {
    console.log('MONGO_URI:', process.env.MONGO_URI);
    if (!process.env.MONGO_URI) {
      throw new Error('MONGO_URI is not defined in the environment variables');
    }
    await mongoose.connect(process.env.MONGO_URI);
    console.log('Connected to MongoDB');

    for (const user of testUsers) {
      const savedUser = await saveTwitterUser(user);
      console.log(`Saved user: ${savedUser.username}`);
    }

    console.log('All test users saved successfully');
  } catch (error) {
    console.error('Error saving test data:', error.message);
  } finally {
    await mongoose.disconnect();
    console.log('Disconnected from MongoDB');
  }
}

// Run the test
saveTestData();