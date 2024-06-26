/**
 * Author: Ozzy (@meetg0d)
 * This file sets up the Express server and connects to MongoDB using Mongoose.
 */

require('dotenv').config({ path: '../.env' });
const express = require('express');
const mongoose = require('mongoose');
const connectDB = require('./db');
const twitterUsersRouter = require('./routes/twitterUsers');

const app = express();

app.use(express.json());
app.use('/api/users', twitterUsersRouter);

mongoose.set('strictQuery', false); // Added this line to address deprecation warning

// Connect to MongoDB using the function from db.js
connectDB()
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
