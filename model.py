from flask import Flask, render_template, url_for, g, redirect, request
import httplib2, redis, sqlite3, tweepy
import settings

auth = tweepy.OAuthHandler(settings.CONSUMER_TOKEN, settings.CONSUMER_SECRET)

app = Flask(__name__)

class TweetNet(object):
	"""
	a TweetNet has a master account
	it also has a number of slave accounts
	the master account can make the slave accounts retweet something by using a callsign in a tweet
	"""

	def tweet_out(self, tweet):
		for slave in self.slaves:
			slave.tweet(tweet)
		return True

	def add_account(self, account):
		try:
			self.slaves.append(account)
			return True
		except:
			return False

	def __init__(self, name, account, callsign):
		self.name = name
		self.master = account
		self.callsign = callsign
		self.slaves = []

class Account(object):
	"""
	a twitter account
	"""

	def tweet(self, tweet):
		#set up the access credentials
		auth = tweepy.OAuthHandler(settings.CONSUMER_TOKEN, settings.CONSUMER_SECRET)
		auth.set_access_token(self.access_key, self.access_secret)

		#now do the tweet
		api = tweepyAPI(auth)
		api.retweet(tweet)

		return True

	def authorise_callback(self):
		"""
		finishes off the authorisation process (once a user has come back to us)
		"""
		verifier = request.GET.get('oauth_verifier')

		auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
		token = session.request_token
		auth.set_request_token(token.key, token.secret)

		auth.get_access_token(verifier)

		self.access_key = auth.access_token.key
		self.access_secret = auth.access_token.secret

	def authorise(self):
		"""
		starts the authorisation process.
		"""
		auth = tweepy.OAuthHandler(settings.CONSUMER_TOKEN, settings.CONSUMER_SECRET, settings.CALLBACK_URL)

		session.request_token = {'key': auth.request_token.key, 'secret': auth.request_token.secret}

		return redirect(auth.get_authorization_url())

	def __init__(self):
		"""
		TODO: twitter account stuff goes here
		"""
		return authorise()