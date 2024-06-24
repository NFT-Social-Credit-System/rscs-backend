/**
 * Author: Ozzy (@meetg0d)
 * This file sets up the Express server and connects to MongoDB using Mongoose.
 */

require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const twitterUsersRouter = require('./routes/twitterUsers');

const app = express();

app.use(express.json());
app.use('/api/twitter-users', twitterUsersRouter);

mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('MongoDB connection error:', err));

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
