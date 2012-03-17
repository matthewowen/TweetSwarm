from flask import Flask, render_template, session, url_for, g, redirect, request

import tweepy, settings, sqlite3, model

DATABASE = 'db'

app = Flask(__name__)

app.secret_key = settings.SECRET_KEY

# UTILITIES

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

def connect_db():
    return sqlite3.connect(DATABASE)

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

# ERRORS

@app.errorhandler(404)
def page_not_found(error):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	return render_template('500.html'), 500

# TWITTER AUTH

@app.route('/auth/')
def twitter_auth():
	t = model.Account()
	return t.authorise()

@app.route('/auth/callback')
def callback():
	#do the callback stuff
	t = model.Account()
	return t.authorise_callback()

# INPUT

@app.route('/tweetnets/<tweetnet>/', methods=['GET', 'POST'])
def botnet(tweetnet):
	"""
	if get, tweetnet info
	if post, add account to tweetnet
	"""
	q = query_db('SELECT * FROM tweetnets WHERE (name=?);', [tweetnet], one=True)
	t = model.TweetNet(q['name'], q['master_account'], q['callsign'])

	if request.method == 'POST':
		try:
			t.add_account()
			return render_template('tweetnet.html', tweetnet=t, joined=True, token=session['account'][0], message='Your Twitter account was successfully added to this TweetNet')
		except KeyError:
			session['tweetnet'] = tweetnet
			return redirect('/auth/')
	else:
		try:
			if query_db('SELECT * FROM tweetnetaccount WHERE (account_id=? AND tweetnet=?);', [session['account'][0], tweetnet]):
				return render_template('tweetnet.html', tweetnet=t, joined=True, token=session['account'][0])
			else:
				pass
		except KeyError:
			pass
		return render_template('tweetnet.html', tweetnet=t)

@app.route('/tweetnets/<tweetnet>/<access_key>/', methods=['POST'])
def botnet_account(tweetnet, access_key):
	q = query_db('SELECT * FROM tweetnets WHERE (name=?);', [tweetnet], one=True)
	t = model.TweetNet(q['name'], q['master_account'], q['callsign'])

	r = t.remove_account(access_key)

	if r:
		return render_template('tweetnet.html', tweetnet=t, message='Your Twitter account has been removed from this TweetNet')
	else:
		return render_template('tweetnet.html', tweetnet=t, error='Something went wrong with removing your Twitter account from this TweetNet')

@app.route('/tweetnets/', methods=['GET', 'POST'])
def botnets():
	"""
	if get, tweetnet listing page
	if post, create a tweetnet
	"""
	if request.method == 'POST':
		tweetnet = model.TweetNet(request.form['name'], request.form['account'], request.form['callsign'])
		tweetnet.save()
		return redirect('/tweetnets/')
	else:
		tweetnets = query_db('SELECT * FROM tweetnets;')
		tweetnets.reverse()
		return render_template('tweetnets.html', tweetnets=tweetnets)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/about/')
def about():
	return render_template('about.html')

@app.route('/do/')
def do_tweets():
	q = query_db('SELECT * FROM tweetnets')
	for r in q:
		t = model.TweetNet(r['name'], r['master_account'], r['callsign'])
		t.do_tweets()
	return redirect('/')

# RUN CONFIG

if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    import os
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/': os.path.join(os.path.dirname(__file__), 'static')
    })

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)