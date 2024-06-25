#!/usr/bin/env python3

from collections import defaultdict
import hashlib 

class Investment:
	def __init__(self, investment_name, value, owner):
		self.owner = owner
		self.investment_name = investment_name
		self.market_cap = 0
		self.coins_value = value
		self.investors = []
		self.sum_of_investors = 0
	
	def get_name(self):
		return self.investment_name
	
	def get_coin(self):
		return self.coins_value
	
	def get_marketcap(self):
		return self.market_cap
	
	def get_owner(self):
		return self.owner
	
	def get_investors(self):
		return self.investors
	
	def get_sum_investors(self):
		return self.sum_of_investors
	
class Wallet:
	def __init__(self):
		self.pending_transactions = {}
		self.approved_transactions = {}
		self.active_investments = {}
		self.investment_vector = []
		self.settled_cash = 100
		self.coins = 0
		
		
	def set_active_investment(self, name, value):
		self.active_investments[name] = value
		
	def set_settled_cash(self, value):
		self.settled_cash = value
		
	def set_coins(self, value):
		self.coins = value
		
	def get_active_investment(self, name):
		return self.active_investments[name]
	
	def get_settled_cash(self):
		return self.settled_cash
	
	def get_coins(self):
		return self.coins
	
	def sell_coins(self, amount):
		self.settled_cash += amount
		
	def buy_coins(self, amount):
		self.settled_cash -= amount
		self.coins += amount
		
	def get_active_investments(self):
		return sum(self.investment_vector)
	
class Client:
	def __init__(self):
		self.username = ""
		self.password = ""
		self.wallet = Wallet()
		self.public_key = ""
		self.stake = 0
		
	def set_stake(self, value):
		self.stake = value
		
	def set_username(self, value):
		self.username = value
		
	def set_password(self, value):
		self.password = value
		
	def set_public_key(self, value):
		self.public_key = value
		
	def get_stake(self):
		return self.stake
	
	def get_username(self):
		return self.username
	
	def get_password(self):
		return self.password
	
	def get_public_key(self):
		return self.public_key
	
	def make_investment(self, value, invest):
		self.wallet.set_active_investment(invest.investment_name, value)
		invest.investors.append({'name':invest.investment_name,'value':value}) #[invest.investment_name] = value
		bal = self.wallet.get_settled_cash()
		new_bal = bal - value
		self.wallet.set_settled_cash(new_bal)
		self.wallet.active_investments[invest.investment_name] = bal
		self.wallet.investment_vector.append(value)
		invest.market_cap += bal
		invest.sum_of_investors += 1
		
	def sell_investment(self, value, invest):
		self.wallet.active_investments[invest.investment_name] = 0
		bal = self.wallet.get_settled_cash()
		invest.market_cap -= bal
		
	def convert_stake(self):
		s = self.stake
		self.wallet.coins += s
		self.stake = 0
		
class Coin:
	def __init__(self):
		self.market_cap = 0.0001
		self.staked_coins = []
		self.new_coins = 0
		self.dollar_value = 0
		
	def process_coins(self):
		self.new_coins += 1
		return self.new_coins
	
	def set_dollar_value(self, value):
		self.dollar_value = value
		
	def get_dollar_value(self):
		return self.dollar_value
	
	def stake_coins(self, approved_transactions, pending_transactions, sender):
		v = self.process_coins()
		len1 = len(pending_transactions)
		len2 = len(approved_transactions)
		pending_sum = sum(pending_transactions)
		approved_sum = sum(approved_transactions)
		total_sum = pending_sum + approved_sum
		u = (len1 + len2) / total_sum * v
		return u
	
class Network:
	def __init__(self):
		self.pending_transactions = []
		self.approved_transactions = []
		self.stake = []
		self.web = defaultdict(float)
		self.senders = []
		self.money = []
		self.recipients = []
		self.market_cap = 0.0001
		
	def set_market_cap(self, value):
		self.market_cap = value
		
	def get_market_cap(self):
		return self.market_cap
	
	def get(self):
		for i in range(len(self.senders)):
			print("senders\t", self.senders[i])
			print("recipients\t", self.recipients[i])
			print("money\t", self.money[i])
			
	def get_stake(self):
		for s in self.stake:
			print("get stake\t", s)
			
	def get_pending(self):
		for p in self.pending_transactions:
			print("get pending\t", p)
			
	def get_approved(self):
		for a in self.approved_transactions:
			print("get approved\n", a)
			
	def set_transaction(self, sender, recv, value):
		sender_user = sender.get_public_key()
		recv_public_key = recv.get_public_key()
		money = value
		bal = sender.wallet.get_settled_cash()
		new_bal = bal - value
		sender.wallet.set_settled_cash(new_bal)
		self.senders.append(sender.get_username())
		self.money.append(value)
		self.recipients.append(recv.get_public_key())
		self.pending_transactions.append({'sender':sender_user,'recv':recv_public_key,'amount':value})
		
	def process_transaction(self, sender, recv, value, index, c):
		self.get_transaction(sender, recv, value)
		self.approved_transactions.append(value) #{'sender':sender.get_public_key(),'recv':recv.get_public_key(),'amount':value})
		self.pending_transactions.pop(index)
		self.web[recv.get_public_key()] += value
		result = c.stake_coins(self.approved_transactions, self.money, sender)
		self.stake.append(result)
		gained_coins = sender.wallet.get_coins() + result
		print("gained coins", gained_coins)
		c.market_cap += gained_coins
		self.market_cap += gained_coins
		return gained_coins
	
	def get_transaction(self, sender, recv, value):
		if sender.wallet.get_settled_cash() >= value:
			bal = recv.wallet.get_settled_cash()
			new_bal = bal + value
			recv.wallet.set_settled_cash(new_bal)
		else:
			bal = sender.wallet.get_settled_cash()
			new_bal = bal + value
			sender.wallet.set_settled_cash(new_bal)
			
class Validator(Client):
	def __init__(self):
		super().__init__()
		self.receipt_hash = []
		self.receipt = []
		self.ledger = {}
		self.ledger_hash = {}
		
	def mine_block(self, net, sender, recv, value, index, c):
		staked_coins = net.get_market_cap()
		earned_coins = net.process_transaction(sender, recv, value, index, c)
		c.market_cap += staked_coins + earned_coins
		self.ledger[sender.get_username()] = earned_coins
		self.receipt.append(earned_coins)
		return earned_coins
	
	def process_receipts(self):
		total_sum = sum(self.receipt)
		self.stake += total_sum
		self.receipt.clear()
		return total_sum
	
	def hashing_double(self, value):
		hashed_data = hashlib.sha256(value).hexdigest()
		return hashed_data#int.from_bytes(self.receipt_hash.update(str(value).encode()).digest(), byteorder='big')
	
	