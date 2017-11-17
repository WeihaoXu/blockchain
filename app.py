import sys
import hashlib
import json
import flask
from flask import Flask, jsonify, request
from flask.views import MethodView
from datatypes import Block, BlockChain, Transaction
from threading import Lock
from flask import current_app
import requests

import nodedata
from nodedata import blockchain, transaction_pool, done_transactions 
from nodedata import MAX_TX_PER_BLOCK, get_blockchain_for_view




class Mine(MethodView):
    def get(self):
        while True:
            print("mining")
            txs_to_include = self.select_transaction_set()
            with blockchain.lock:
                block = blockchain.mine_block(current_app.config['port'], list(txs_to_include))
                if blockchain.validate_new_block(block):
                    blockchain.add_block(block)
                    self.broadcast_new_block(block)
                    with transaction_pool.lock:
                        transaction_pool.transactions-= txs_to_include
                    done_transactions.update(txs_to_include)

    def select_transaction_set(self):
        selected = set()
        with transaction_pool.lock:
            for tx in transaction_pool.transactions:
                selected.add(tx)
                if(len(selected) == MAX_TX_PER_BLOCK):
                    break
            return selected


    def broadcast_new_block(self, block):
        block_dict = block.to_dict()
        current_port = current_app.config['port']
        ports = current_app.config['port_list']
        for peer_port in ports:
            if peer_port == current_port:
                continue
            self.send_Block_Info(peer_port, block_dict)

    def send_Block_Info(self, port, block_dict):
        try:
            message = {
                'miner': current_app.config['port'],
                'block': block_dict
            }
            url = 'http://localhost:{}/receive_block'.format(port)
            res = requests.post(url, data=json.dumps(message))
        except:
            print("send block into to {} faild".format(port))
        
class ReceiveBlock(MethodView):
    def post(self):
        data = flask.request.data
        data = json.loads(data.decode('utf-8'))
        print(data)
        block = Block.retrive_from_dict(data['block'])
        with blockchain.lock:
            if blockchain.validate_new_block(block):
                blockchain.add_block(block)
        return 'ok', 200
        
    
  
class ReceiveTransaction(MethodView):
    def post(self):
        data = flask.request.form
        sender = data.get('sender')
        receiver = data.get('receiver')
        value = data.get('value')
        timestamp = data.get('timestamp')
        tx = Transaction(sender, receiver, value, timestamp=timestamp) # retrive from post
        with transaction_pool.lock:
            if (tx in transaction_pool.transactions) or (tx in done_transactions):
                print("receive duplicate transaction")
                return 'duplicate transactions', 200
            transaction_pool.transactions.add(tx)
        self.broadcast_tx_req(tx)
        return 'ok', 200

    def broadcast_tx_req(self, tx):
        tx_dict = tx.to_dict()
        current_port = current_app.config['port']
        ports = current_app.config['port_list']
        for peer_port in ports:
            if peer_port == current_port:
                continue
            self.send_tx_req(peer_port, tx_dict)

    def send_tx_req(self, port, tx_dict):
        try:
            url = 'http://localhost:{}/receive_transaction'.format(port)  
            session = requests.Session()  
            session.post(url, data=tx_dict)
        except:
            print("send transaction from {} to {} faild".
                    format(current_app.config['port'], port))
        
            

class ViewChain(MethodView):
    def get(self):
        blockchain = get_blockchain_for_view()
        return jsonify(blockchain), 200


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise(Exception('please run CMD: python app.py <PORT> <PORT_LIST>'))
    port = sys.argv[1]
    port_list = sys.argv[2].split()
    app = Flask("node_" + port) 
    app.config.update(DEBUG=True)
    app.config['port'] = port
    app.config['port_list'] = port_list
    app.add_url_rule('/mine', view_func=Mine.as_view('mine'))
    app.add_url_rule('/receive_transaction', view_func=ReceiveTransaction.as_view('receive_transaction'))
    app.add_url_rule('/view', view_func=ViewChain.as_view('view'))
    app.add_url_rule('/receive_block', view_func=ReceiveBlock.as_view('receive_block'))
    app.run(host=nodedata.HOST, port=int(port), threaded=True, use_debugger=True)
