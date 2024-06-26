/**
 * Author: Ozzy (@meetg0d)
 * This file defines the Mongoose schema for Twitter user data.
 */

const mongoose = require('mongoose');

const TwitterUserSchema = new mongoose.Schema({
  username: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  profilePictureUrl: { type: String },
  followersCount: { type: Number, default: 0 },
  score: {
    up: { type: Number, default: 0 },
    down: { type: Number, default: 0 }
  },
  status: { type: String, enum: ['Approved', 'Moderate', 'Risk'], default: 'Moderate' },
  isRemiliaOfficial: { type: Boolean, default: false },
  isMiladyOG: { type: Boolean, default: false },
  hasGoldenBadge: { type: Boolean, default: false },
  isClaimed: { type: Boolean, default: false }
});

module.exports = mongoose.model('TwitterUser', TwitterUserSchema);