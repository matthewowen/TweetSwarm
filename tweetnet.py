from flask import Flask, render_template, session, url_for, g, redirect, request

import model
import settings

app = Flask(__name__)

app.secret_key = settings.SECRET_KEY

# UTILITIES
"""
@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()
"""
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

@app.route('/tweetnets/<tweetnet>', methods=['GET', 'POST'])
def botnet(tweetnet):
	"""
	if get, tweetnet info
	if post, add to tweetnet
	"""
	if request.method == 'POST':
		tweetnet.add_account(account)
		return render_template('account_added.html')
	else:
		return render_template('tweetnet.html')

@app.route('/tweetnets/', methods=['GET', 'POST'])
def botnets():
	"""
	if get, tweetnet creation page
	if post, create a tweetnet
	"""
	if request.method == 'POST':
		tweetnet = TweetNet(request.form['name'], request.form['account'], request.form['callsign'])
		return redirect#TODO
	else:
		return render_template('create_tweetnet.html')

@app.route('/')
def home():
	return render_template('home.html')

# RUN CONFIG

if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    import os
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      '/': os.path.join(os.path.dirname(__file__), 'static')
    })

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)