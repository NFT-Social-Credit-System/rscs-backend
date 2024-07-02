/**

 * Author: Ozzy (@meetg0d)

 * This file sets up the Express server and connects to MongoDB using the native MongoDB driver.

 */



require('dotenv').config({ path: '../.env' });

const express = require('express');

const { connectDB } = require('./db');

const twitterUsersRouter = require('./routes/twitterUsers');



const app = express();

const PORT = process.env.PORT || 3000;



app.use(express.json());

app.use('/api/users', twitterUsersRouter);
app.use('/api/scrape', require('./routes/scrape'));



// Connect to MongoDB using the function from db.js
connectDB()
  .then(() => {
    console.log('Connected to MongoDB');
    app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
  })
  .catch(err => {
    console.error('MongoDB connection error:', err);
    console.error('Error details:', JSON.stringify(err, null, 2));
    process.exit(1);
  });