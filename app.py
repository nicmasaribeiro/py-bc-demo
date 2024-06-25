from flask import Flask, render_template, request, redirect, abort, jsonify,sessions, Response,url_for
from flask import Blueprint
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel, db, login, StockModel
import stripe
import os
import random
import yfinance
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import io
import json
import plotly
import plotly.express as px
from flask_migrate import Migrate
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from werkzeug import *
import requests
from scipy.stats.mstats import gmean
from classes import *

investments = []
clients = []
validators = []
network = Network()
coin = Coin()

exchange_rate = network.market_cap/coin.market_cap

app = Flask(__name__)
app.secret_key = 'xyz'

stripe.api_key = 'sk_test_51OncNPGfeF8U30tWYUqTL51OKfcRGuQVSgu0SXoecbNiYEV70bb409fP1wrYE6QpabFvQvuUyBseQC8ZhcS17Lob003x8cr2BQ'
stripe_publishable_key = 'pk_test_51OncNPGfeF8U30tWN8a2tFbG6LZmaztpX884D1WVkXqpIBQBqEC5DCAIl2LYeHeaCKWp5Kje4B5jvWX7pT9HzViG00cu7dduBP'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/dcf'

db.init_app(app)
login.init_app(app)
login.login_view = 'login'

Migrate(app,db)

with app.app_context():
	db.create_all()
	users = UserModel.query.all()
	print(users)

@app.route('/')
def base():
	return render_template('base.html')

@app.route('/index')
def index():
	return render_template('index.html')

@app.route('/indextwo')
def indextwo():
	return render_template('indextwo.html')

@app.route('/create-user/<name>/<password>/<pk>')
def create_user(name,password,pk):
	clients.append(Client())
	clients[-1].set_username(name)
	clients[-1].set_password(password)
	clients[-1].set_public_key(pk)
	number = len(clients) - 1
	public_key = pk + str(number)
	clients[-1].set_public_key(public_key)
	return redirect('/')

@app.route('/get-users')
def get_users():
	return render_template('users.html', users=clients)

@app.route('/create-val/<name>/<password>/<pk>')
def create_val(name,password,pk):
	validators.append(Validator())
	validators[-1].set_username(name)
	validators[-1].set_password(password)
	number = len(validators) - 1
	public_key = pk + str(number)
	validators[-1].set_public_key(public_key)
	return redirect('/')

@app.route('/get-vals')
def get_vals():
	return render_template('validators.html', vals=validators)

@app.route('/user/<key>/<password>')
def user_home(key,password):
	index = int(key)
	c = clients[index]
	pwd = c.get_password()
	if pwd == password:
		return render_template('userhome.html',client=c)
	else:
		return redirect('/')

@app.route('/usercred')
def user_cred():
	return render_template('user-cred.html')

@app.route('/set-transaction/<senderkey>/<recipientkey>/<amount>')
def set_transaction(senderkey,recipientkey,amount):
	i = int(senderkey)
	ii = int(recipientkey)
	sender = clients[i]
	recipient = clients[ii]
	network.set_transaction(sender, recipient, float(amount))
	return redirect('/')

@app.route('/get-pending')
def get_pending():
	trans = network.pending_transactions
	return render_template('pending-transactions.html',transactions=trans)

@app.route('/mine/<valkey>/<senderkey>/<recipientkey>/<amount>/<transkey>')
def mine(valkey,senderkey,recipientkey,amount,transkey):
	trans = network.pending_transactions[int(transkey)]
	print(trans['amount'])
	if (trans['amount'] == float(amount)): #and (trans[''])
		v = int(valkey)
		i = int(senderkey)
		ii = int(recipientkey)
		sender = clients[i]
		recipient = clients[ii]
		val = validators[v]
		val.mine_block(network, sender, recipient, float(amount), int(transkey), coin)
		val.process_receipts()
		val.convert_stake()
		return redirect('/valcred')
	else:
		return redirect('/')

@app.route('/val/<key>/<password>')
def val_info(key,password):
	index = int(key)
	validator = validators[index]
	pwd = validator.get_password()
	if pwd == password:
		return render_template('valhome.html',validator=validator)
	else:
		return redirect('/')

@app.route('/valcred')
def val_cred():
	return render_template('val-cred.html')


@app.route('/transact')
def transact():
	return render_template('transact.html')

@app.route('/minetrans')
def mine_trans():
	return render_template('mine.html')

@app.route('/cmc')
def cmc():
	mk = network.market_cap
	marketcap = coin.market_cap
	return render_template('cmc.html',cmc=marketcap,nmc=mk)

@app.route('/create-investment/<name>/<value>/<ownerindex>')
def create_investment(ownerindex,name,value):
	investments.append(Investment(name, value, clients[int(ownerindex)]))
	return redirect('/')

@app.route('/create-inv')
def create_investment_page():
	return render_template('create-investment.html')

@app.route('/investments')
def get_investments():
	return render_template('investments-list.html',invs=investments)

@app.route('/make-investment/<value>/<investindex>/<buyerindex>')
def make_investment(investindex,value,buyerindex):
	cli = clients[int(buyerindex)]
	cli.make_investment(float(value), investments[int(investindex)])
	return redirect('/')

@app.route('/make-inv')
def make_investment_page():
	return render_template('make-investment.html')
	
app.run(debug=True,host='0.0.0.0',port=8000)