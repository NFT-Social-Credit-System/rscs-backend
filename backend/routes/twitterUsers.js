/**
 * Author: Ozzy (@meetg0d)
 * This file defines the route for saving Twitter user data.
 */

const express = require('express');
const router = express.Router();
const User = require('../models/TwitterUserData');

// Get all users
router.get('/', async (req, res) => {
  console.log('Received request to fetch all users');
  try {
    const users = await User.find();
    console.log(`Fetched ${users.length} users from the database`);
    res.json(users);
  } catch (error) {
    console.error('Error fetching users:', error);
    res.status(500).json({ message: error.message });
  }
});

// Create a new user
router.post('/', async (req, res) => {
  console.log('Received request to create new user:', req.body);
  try {
    const { username } = req.body;
    const newUser = new User({ username });
    await newUser.save();
    console.log('New user created:', newUser);
    res.status(201).json(newUser);
  } catch (error) {
    console.error('Error creating new user:', error);
    res.status(400).json({ message: error.message });
  }
});

// Upvote a user
router.post('/:id/upvote', async (req, res) => {
  console.log(`Received request to upvote user with id: ${req.params.id}`);
  try {
    const user = await User.findById(req.params.id);
    if (!user) {
      console.log(`User with id ${req.params.id} not found`);
      return res.status(404).json({ message: 'User not found' });
    }
    user.score.up += 1;
    await user.save();
    console.log(`User ${user.username} upvoted successfully`);
    res.json(user);
  } catch (error) {
    console.error('Error upvoting user:', error);
    res.status(400).json({ message: error.message });
  }
});

// Downvote a user
router.post('/:id/downvote', async (req, res) => {
  try {
    const user = await User.findById(req.params.id);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    user.score.down += 1;
    await user.save();
    res.json(user);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
});

module.exports = router;