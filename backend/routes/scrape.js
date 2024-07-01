const express = require('express');
const router = express.Router();
const axios = require('axios');

const FLASK_API_URL = 'http://18.199.167.152:5000';

router.post('/', async (req, res) => {
  const { username } = req.body;
  
  try {
    const response = await axios.post(`${FLASK_API_URL}/scrape`, { username });
    res.status(200).json({ message: `Scraping completed for "${username}"`, data: response.data });
  } catch (error) {
    console.error('Error calling Flask API:', error);
    res.status(500).json({ message: 'Error processing scraped data' });
  }
});

module.exports = router;
