/**
 * Author: Ozzy (@meetg0d)
 * This file defines the Mongoose schema for Twitter user data.
 */

const mongoose = require('mongoose');

const TwitterUserSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  displayName: { type: String, required: true },
  profilePictureUrl: { type: String, required: true },
  followersCount: { type: Number, required: true }
});

module.exports = mongoose.model('TwitterUser', TwitterUserSchema);