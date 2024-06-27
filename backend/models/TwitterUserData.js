const { ObjectId } = require('mongodb');

const TwitterUser = {
  username: String,
  display_name: String,
  pfp_url: String,
  followers: String,
  following: String,
  website: String,
  description: String,
  location: String,
  join_date: String,
  birth_date: String,
  score: {
    up: { type: Number, default: 0 },
    down: { type: Number, default: 0 }
  },
  votes: [{
    voter: String,
    weight: Number,
    voteType: String,
    timestamp: Date
  }],
  status: { type: String, default: 'unclaimed' },
  isRemiliaOfficial: { type: Boolean, default: false },
  isMiladyOG: { type: Boolean, default: false },
  hasGoldenBadge: { type: Boolean, default: false },
  isClaimed: { type: Boolean, default: false }
};

module.exports = TwitterUser;
