/**
 * Author: Ozzy (@meetg0d)
 * This file defines the route for saving Twitter user data.
 */

const express = require('express');
const router = express.Router();
const { saveTwitterUser } = require('../services/scweetService');

router.post('/save', async (req, res) => {
  try {
    const user = await saveTwitterUser(req.body);
    res.json({ success: true, user });
  } catch (error) {
    console.error('Error in /save route:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;