const { ObjectId } = require('mongodb');

const TwitterUser = {
  username: String,
  name: String,
  profilePictureUrl: String,
  followersCount: Number,
  score: {
    up: Number,
    down: Number
  },
  votes: [{
    voter: String,
    weight: Number,
    voteType: String,
    timestamp: Date
  }],
  status: String,
  isRemiliaOfficial: Boolean,
  isMiladyOG: Boolean,
  hasGoldenBadge: Boolean,
  isClaimed: Boolean
};

module.exports = TwitterUser;
