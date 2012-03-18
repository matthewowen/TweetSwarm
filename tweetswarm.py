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

@app.route('/tweetswarms/<tweetswarm>/', methods=['GET', 'POST'])
def botnet(tweetswarm):
	"""
	if get, tweetswarm info
	if post, add account to tweetswarm
	"""
	q = query_db('SELECT * FROM tweetswarm WHERE (name=?);', [tweetswarm], one=True)
	t = model.TweetSwarm(q['name'], q['master_account'], q['callsign'])

	if request.method == 'POST':
		try:
			t.add_account()
			return render_template('tweetswarm.html', tweetswam=t, joined=True, token=session['account'][0], message='Your Twitter account was successfully added to this TweetSwarm')
		except KeyError:
			session['tweetswarm'] = tweetswarm
			return redirect('/auth/')
	else:
		try:
			if query_db('SELECT * FROM tweetswarmaccount WHERE (account_id=? AND tweetswarm=?);', [session['account'][0], tweetswarm]):
				return render_template('tweetswarm.html', tweetswarm=t, joined=True, token=session['account'][0])
			else:
				pass
		except KeyError:
			pass
		return render_template('tweetswarm.html', tweetswarm=t)

@app.route('/tweetswarms/<tweetswarm>/<access_key>/', methods=['POST'])
def botnet_account(tweetswarm, access_key):
	q = query_db('SELECT * FROM tweetswarms WHERE (name=?);', [tweetswarm], one=True)
	t = model.tweetswarm(q['name'], q['master_account'], q['callsign'])

	r = t.remove_account(access_key)

	if r:
		return render_template('tweetswarm.html', tweetswarm=t, message='Your Twitter account has been removed from this tweetswarm')
	else:
		return render_template('tweetswarm.html', tweetswarm=t, error='Something went wrong with removing your Twitter account from this tweetswarm')

@app.route('/tweetswarms/', methods=['GET', 'POST'])
def botnets():
	"""
	if get, tweetswarm listing page
	if post, create a tweetswarm
	"""
	if request.method == 'POST':
		tweetswarm = model.tweetswarm(request.form['name'], request.form['account'], request.form['callsign'])
		tweetswarm.save()
		return redirect('/tweetswarms/')
	else:
		tweetswarms = query_db('SELECT * FROM tweetswarms;')
		tweetswarms.reverse()
		return render_template('tweetswarms.html', tweetswarms=tweetswarms)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/about/')
def about():
	return render_template('about.html')

@app.route('/do/')
def do_tweets():
	q = query_db('SELECT * FROM tweetswarms')
	for r in q:
		t = model.tweetswarm(r['name'], r['master_account'], r['callsign'])
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