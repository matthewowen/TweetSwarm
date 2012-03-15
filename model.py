from flask import Flask, render_template, url_for, g, redirect, request
import httplib2, redis, sqlite3

app = Flask(__name__)

class TweetNet(object):
	"""
	a TweetNet has a controlling account
	it also has a number of controlled accounts
	the controlling account can make the controlled accounts retweet something
	"""

	def __init__(self, name, account):
		self.name = name
		self.controllingAccount = account


class Account(object):
	"""
	a twitter account
	"""