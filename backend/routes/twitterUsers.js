/**
 * Author: Ozzy (@meetg0d)
 * This file defines the route for saving Twitter user data.
 */

const express = require('express');
const router = express.Router();
const { getConnection } = require('../db');

const db = getConnection();

// Get all users
router.get('/', async (req, res) => {
  console.log('Received request to fetch all users');
  try {
    const usersCollection = db.collection('users');
    const users = await usersCollection.find().toArray();
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
    const usersCollection = db.collection('users');
    await usersCollection.insertOne({ username });
    console.log('New user created:');
    res.status(201).json({ username });
  } catch (error) {
    console.error('Error creating new user:', error);
    res.status(400).json({ message: error.message });
  }
});

// Upvote a user
router.post('/:id/upvote', async (req, res) => {
  console.log(`Received request to upvote user with id: ${req.params.id}`);
  try {
    const usersCollection = db.collection('users');
    const user = await usersCollection.findOneAndUpdate(
      { _id: req.params.id },
      { $inc: { 'score.up': 1 } },
      { returnDocument: 'after' }
    );
    if (!user.value) {
      console.log(`User with id ${req.params.id} not found`);
      return res.status(404).json({ message: 'User not found' });
    }
    console.log(`User ${user.value.username} upvoted successfully`);
    res.json(user.value);
  } catch (error) {
    console.error('Error upvoting user:', error);
    res.status(400).json({ message: error.message });
  }
});

// Downvote a user
router.post('/:id/downvote', async (req, res) => {
  try {
    const usersCollection = db.collection('users');
    const user = await usersCollection.findOneAndUpdate(
      { _id: req.params.id },
      { $inc: { 'score.down': 1 } },
      { returnDocument: 'after' }
    );
    if (!user.value) {
      return res.status(404).json({ message: 'User not found' });
    }
    res.json(user.value);
  } catch (error) {
    res.status(400).json({ message: error.message });
  }
});

module.exports = router;