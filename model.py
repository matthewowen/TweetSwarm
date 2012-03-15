from flask import Flask, render_template, url_for, g, redirect, request
import httplib2, redis, sqlite3

app = Flask(__name__)

class TweetNet(object):
	"""
	a TweetNet has a controlling account
	it also has a number of controlled accounts
	the controlling account can make the controlled accounts retweet something
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
		#tweet the tweet here
		return True

	def __init__(self, id):
		"""
		TODO: twitter account stuff goes here