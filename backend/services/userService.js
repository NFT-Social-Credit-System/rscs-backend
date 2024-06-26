const { getConnection } = require('../db');

const saveUser = async (userData) => {
  try {
    const db = getConnection();
    const usersCollection = db.collection('users');

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
    
    const result = await usersCollection.findOneAndUpdate(
      { username },
      { 
        $set: { 
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
        }
      },
      { upsert: true, returnDocument: 'after' }
    );

    return result.value;
  } catch (error) {
    console.error('Error saving user:', error);
    throw error;
  }
};

module.exports = { saveUser };
