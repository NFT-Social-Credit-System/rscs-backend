const TwitterUser = require('../models/TwitterUserData');

const saveUser = async (userData) => {
  try {
    const { 
      username, 
      name, 
      avatarUrl, 
      followers, 
      score, 
      status, 
      isRemiliaOfficial, 
      isMiladyOG,
      hasGoldenBadge,
      isClaimed
    } = userData;
    
    const user = await TwitterUser.findOneAndUpdate(
      { username },
      { 
        username, 
        name, 
        avatarUrl, 
        followers,
        score,
        status,
        isRemiliaOfficial,
        isMiladyOG,
        hasGoldenBadge,
        isClaimed
      },
      { upsert: true, new: true }
    );

    return user;
  } catch (error) {
    console.error('Error saving user:', error);
    throw error;
  }
};

module.exports = { saveUser };
