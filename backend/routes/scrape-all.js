const express = require('express');
const router = express.Router();
const axios = require('axios');
const User = require('../models/User');

const FLASK_API_URL = 'http://18.199.167.152:5000';

router.post('/', async (req, res) => {
  try {
    const users = await User.find({}, 'username');
    const usernames = users.map(user => user.username);

    const response = await axios.post(`${FLASK_API_URL}/scrape-all`, { usernames });
    res.status(200).json({ message: 'Scraping completed for all users', data: response.data });
  } catch (error) {
    console.error('Error calling Flask API:', error);
    res.status(500).json({ message: 'Error processing scraped data' });
  }
});

module.exports = router;
