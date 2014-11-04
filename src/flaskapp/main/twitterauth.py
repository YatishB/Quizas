# Adapted from:
# http://whichlight.com/blog/twitter-oauth-in-python-with-tweepy-and-flask/

import requests
import ast
import json

# Use tweepy to manage Twitter auth stuff.
# See:
# http://tweepy.readthedocs.org/en/v2.3.0/
# Requires tweepy pip package.
import tweepy

import secrets
import authhelper

from flask import Blueprint
from flask import request, redirect

# Use the main blueprint, so that the code is in general tidier.
from . import main


CONSUMER_TOKEN  = secrets.auth["twitter"]["client_id"]
CONSUMER_SECRET = secrets.auth["twitter"]["key_secret"]
CALLBACK_URL    = secrets.auth["twitter"]["redirect_url"]

# Err, should probably be using KVSession??
session = dict()
db = dict() #you can save these values to a database


@main.route("/twitterauth")
def send_token():
	auth = tweepy.OAuthHandler(CONSUMER_TOKEN,
	                           CONSUMER_SECRET,
	                           CALLBACK_URL)
	
	try:
		# get the request tokens
		redirect_url = auth.get_authorization_url()
		session['request_token'] = (auth.request_token.key,
		                            auth.request_token.secret)
	except tweepy.TweepError:
		print 'Error! Failed to get request token'
	
	# this is twitter's url for authentication
	return redirect(redirect_url)




# The Callback
@main.route("/twitterauthstep2")
def get_verification():
	
	#get the verifier key from the request url
	verifier = request.args['oauth_verifier']
	
	auth = tweepy.OAuthHandler(CONSUMER_TOKEN, CONSUMER_SECRET)
	token = session['request_token']
	del session['request_token']
	
	auth.set_request_token(token[0], token[1])

	try:
		auth.get_access_token(verifier)
	except tweepy.TweepError:
		print 'Error! Failed to get access token.'
	
	#now you have access!
	api = tweepy.API(auth)

	#store in a db
	db['api'] = api
	db['access_token_key'] = auth.access_token.key
	db['access_token_secret'] = auth.access_token.secret

	# Now Go to a page where we make use of the Twitter API.
	resp = redirect("http://dev.localhost:8080/twitter_done.html")

	# See http://tweepy.readthedocs.org/en/v2.3.0/auth_tutorial.html#oauth-authentication
	resp.set_cookie("twitter_user_id", auth.access_token.key);
	resp.set_cookie("twitter_access_token", auth.access_token.secret);
	# resp.set_cookie("twitter_expires_in", "???"); # Twitter tokens don't expire

	# Ensure user table has an internal id.
	authhelper.register("twitter:" + auth.access_token.key)

	return resp

# @app.route("/start")
# def start():
# 	#auth done, app logic can begin
# 	api = db['api']
#
# 	#example, print your latest status posts
# 	return flask.render_template('tweets.html', tweets = api.user_timeline())

