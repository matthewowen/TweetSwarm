from flask import Flask, render_template, session, url_for, g, redirect, request
import tweepy, settings, sqlite3, httplib2, json, urllib

DATABASE = 'db'

auth = tweepy.OAuthHandler(settings.CONSUMER_TOKEN, settings.CONSUMER_SECRET)

app = Flask(__name__)

app.secret_key = settings.SECRET_KEY

def connect_db():
    return sqlite3.connect(DATABASE)

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

def tweetswarm_string_validate(s):
	"""
	validates whether a string is of an acceptable format for the TweetSwarm
	"""
	return s.__len__() < 31 and s.__len__() > 0 and not ' ' in s

class TweetSwarm(object):
	"""
	a TweetSwarm has a master account
	it also has a number of slave accounts
	the master account can make the slave accounts retweet something by using a callsign in a tweet
	"""

	def validate(self):
		return tweetswarm_string_validate(self.name) and tweetswarm_string_validate(self.master) and tweetswarm_string_validate(self.callsign)


	def save(self):
		"""
		save object into DB
		"""
		query_db('INSERT INTO tweetswarms VALUES(?,?,?);', [self.name, self.master, self.callsign])
		g.db.commit()

	def do_tweets(self):
		"""
		searches for matching tweets, calls the tweet function for each one
		"""
		http = httplib2.Http()
		url = "http://search.twitter.com/search.json?q=%s+from:%s" % (urllib.quote('#' + self.callsign), urllib.quote(self.master))
		resp, content = http.request(url, "GET")
		d = json.loads(content)
		for j in d['results']:
			self.tweet_out(j['id_str'])

	def tweet_out(self, tweet):
		"""
		for the given tweet, calls the account retweet function for every slave account
		"""
		for i in query_db('SELECT account_id FROM tweetswarmaccount WHERE tweetswarm=?', [self.name]):
			k = query_db('SELECT * from accounts where access_token=?', [i['account_id']], one=True)
			s = Account()
			s.access_key = k['access_token']
			s.access_secret = k['access_secret']
			self.slaves.append(s)
		for slave in self.slaves:
			slave.tweet(tweet)
		return True

	def add_account(self):
		"""
		adds the twitter account belonging to the current user's session
		"""
		account = Account()
		account.access_key = session['account'][0]
		account.access_secret = session['account'][1]
		self.slaves.append(account)
		account.save()
		query_db('INSERT INTO tweetswarmaccount VALUES(?,?);', [account.access_key, self.name])
		g.db.commit()
		return True

	def remove_account(self, access_key):
		"""
		removes a twitter account. requires the passing of an access_key.
		the passed access_key must match the current sessions's access_key
		"""
		account = Account()
		account.access_key = session['account'][0]
		if account.access_key == access_key:
			query_db('DELETE FROM tweetswarmaccount WHERE (account_id=? AND tweetswarm=?);', [account.access_key, self.name])
			g.db.commit()
			return True
		else:
			return False

	def __init__(self, name, master, callsign):
		self.name = name
		self.master = master
		self.callsign = callsign
		self.slaves = []

class Account(object):
	"""
	a twitter account
	"""

	def save(self):
		"""
		saves object into DB
		"""
		try:
			query_db('INSERT INTO accounts VALUES(?,?);', [self.access_key, self.access_secret])
			g.db.commit()
			return True
		except sqlite3.IntegrityError:
			return False

	def tweet(self, tweet):
		"""
		retweets the supplied tweet
		"""
		#set up the access credentials
		auth = tweepy.OAuthHandler(settings.CONSUMER_TOKEN, settings.CONSUMER_SECRET)
		auth.set_access_token(self.access_key, self.access_secret)

		#now do the tweet
		api = tweepy.API(auth)
		api.retweet(tweet)

		return True

	def authorise_callback(self):
		"""
		finishes off the authorisation process (once a user has come back to us)
		"""
		verifier = request.args.get('oauth_verifier')

		auth = tweepy.OAuthHandler(settings.CONSUMER_TOKEN, settings.CONSUMER_SECRET, settings.CALLBACK_URL)
		token = session['request_token']
		auth.set_request_token(token[0], token[1])

		auth.get_access_token(verifier)

		self.access_key = auth.access_token.key
		self.access_secret = auth.access_token.secret

		session['account'] = [self.access_key, self.access_secret]

		self.save

		if session['tweetswarm']:
			q = query_db('SELECT * FROM tweetswarms WHERE (name=?);', [session['tweetswarm']], one=True)
			t = TweetSwarm(q['name'], q['master'], q['callsign'])
			t.add_account()
			return redirect('/tweetswarms/%s' % (session['tweetswarm']))

		return render_template('authorised.html')

	def authorise(self):
		"""
		starts the authorisation process.
		"""
		auth = tweepy.OAuthHandler(settings.CONSUMER_TOKEN, settings.CONSUMER_SECRET, settings.CALLBACK_URL)

		redirect_url = auth.get_authorization_url()

		session['request_token'] = [auth.request_token.key, auth.request_token.secret]

		return redirect(redirect_url)