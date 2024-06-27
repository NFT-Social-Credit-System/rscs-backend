const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');
const path = require('path');

router.post('/', async (req, res) => {
  const { username } = req.body;
  
  const pythonProcess = spawn('python', [
    path.join(__dirname, '..', 'scripts', 'scweet_scraper.py'),
    username
  ]);

  let pythonData = '';

  pythonProcess.stdout.on('data', (data) => {
    pythonData += data.toString();
    console.log(`Python script output: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Python script error: ${data}`);
  });

  pythonProcess.on('close', (code) => {
    console.log(`Python script exited with code ${code}`);
    try {
      const scrapedData = JSON.parse(pythonData);
      res.status(200).json({ message: `Scraping completed for "${username}"`, data: scrapedData });
    } catch (error) {
      console.error('Error parsing Python script output:', error);
      res.status(500).json({ message: 'Error processing scraped data' });
    }
  });
});

module.exports = router;
