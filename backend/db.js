const { MongoClient } = require('mongodb');
require('dotenv').config({ path: '../.env' });

console.log('MONGODB_URI:', process.env.MONGODB_URI);
console.log('Attempting to connect to MongoDB...');

const client = new MongoClient(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

let dbConnection;

const connectDB = async (retries = 5, delay = 5000) => {
  while (retries) {
    try {
      await client.connect();
      dbConnection = client.db('RSCS');
      console.log('MongoDB connected');
      return dbConnection;
    } catch (err) {
      console.error('MongoDB connection error:', err);
      retries -= 1;
      console.log(`Retries left: ${retries}`);
      if (retries === 0) {
        console.error('Could not connect to MongoDB. Exiting...');
        process.exit(1);
      }
      console.log(`Retrying in ${delay / 1000} seconds...`);
      await new Promise(res => setTimeout(res, delay));
    }
  }
};

const getConnection = () => dbConnection;

module.exports = { connectDB, getConnection };
