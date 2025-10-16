const express = require('express');
const mongoose = require('mongoose');
const session = require('express-session');
const MongoStore = require('connect-mongo');
const bcrypt = require('bcryptjs');
const User = require('./models/User');

const app = express();

// Configuration
app.set('view engine', 'ejs');
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// Session
app.use(session({
  secret: 'secret',
  resave: false,
  saveUninitialized: false,
  store: MongoStore.create({ mongoUrl: 'mongodb://mongo:27017/idor-challenge' })
}));

// Routes
app.get('/', (req, res) => {
  res.render('index', { user: req.session.user });
});

app.get('/register', (req, res) => {
  res.render('register');
});

app.post('/register', async (req, res) => {
  const { username, password } = req.body;
  const role = username === 'admin' ? 'admin' : 'user';
  const user = new User({ username, password, role });
  await user.save();
  req.session.user = user;
  res.redirect('/');
});

app.get('/login', (req, res) => {
  res.render('login');
});

app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  const user = await User.findOne({ username });
  if (user && await bcrypt.compare(password, user.password)) {
    req.session.user = user;
    res.redirect('/');
  } else {
    res.redirect('/login');
  }
});

app.get('/users/:id', async (req, res) => {
  // Vulnérabilité IDOR : pas de vérification de rôle ou de propriété
  const user = await User.findById(req.params.id);
  res.render('profile', { user });
});

app.get('/logout', (req, res) => {
  req.session.destroy();
  res.redirect('/');
});

// Démarrage
mongoose.connect('mongodb://mongo:27017/idor-challenge')
  .then(() => {
    app.listen(3000, () => console.log('Server running on http://localhost:3000'));
  });
