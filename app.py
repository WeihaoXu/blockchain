import sys
import hashlib
import json
import flask
from flask import Flask, jsonify, request
from flask.views import MethodView
from datatypes import Block, BlockChain, Transaction
from threading import Lock, Thread
from flask import current_app
import requests
import traceback

import nodedata
from nodedata import blockchain, transaction_pool, done_transactions 
from nodedata import MAX_TX_PER_BLOCK, get_blockchain_for_view




class Mine(MethodView):
    is_mining = False
    def get(self):
        if not self.is_mining:
            current_port = current_app.config['port']
            port_list = current_app.config['port_list']
            self.is_mining = True
            Thread(target=self.mine, args=(current_port, port_list)).start()
            return "mining", 200 
    def mine(self, current_port, port_list):
        while True:
            print("mining")
            txs_to_include = self.select_transaction_set()
            block = blockchain.mine_block(current_port, list(txs_to_include))
            with blockchain.lock:
                if blockchain.validate_new_block(block):
                    blockchain.add_block(block)
                    self.broadcast_new_block(block, current_port, port_list)
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


    def broadcast_new_block(self, block, current_port, ports):
        block_dict = block.to_dict()
        for peer_port in ports:
            if peer_port == current_port:
                continue
            Thread(target=self.send_block_info, 
                        args=(current_port, peer_port, block_dict)).start()

    def send_block_info(self, current_port, peer_port, block_dict):
        try:
            message = {
                'miner': current_port,
                'block': block_dict,
                'chain_length': blockchain.get_length()
            }
            url = 'http://localhost:{}/receive_block'.format(peer_port)
            res = requests.post(url, data=json.dumps(message))
        except Exception as e:
            print("send block info from {} to {} faild".format(current_port, peer_port))
            print(e)
        
class ReceiveBlock(MethodView):
    def post(self):
        data = flask.request.data
        data = json.loads(data.decode('utf-8'))
        block = Block.retrive_from_dict(data['block'])
        with blockchain.lock:
            if blockchain.validate_new_block(block):
                blockchain.add_block(block)
                self.update_done_txs(set(block.transactions))
                return 'ok', 200
        if int(data['chain_length']) > blockchain.get_length():
            Thread(target=self.merge_chain_from_peer, args=(data['miner'], )).start()
            return 'copy chain from you', 200
        else:
            print("validate other's block failed")
            return "rejected ", 200

    def merge_chain_from_peer(self, port):
        print ("merge_chain called")
        url = 'http://localhost:{}/chain'.format(port)
        res = requests.get(url).json()
        received_block_dicts = res['chain']['blocks']
        received_blocks = []
        for block_dict in received_block_dicts:
            block = Block.retrive_from_dict(block_dict)
            received_blocks.append(block)
        received_chain = BlockChain(received_blocks) 
        with blockchain.lock:
            if not received_chain.validate_chain():
                return
            blockchain.blocks = received_blocks
            received_transactions = received_chain.get_transactions()
            with transaction_pool.lock:
                done_transactions = received_transactions
                transaction_pool.transactions -= done_transactions

    def update_done_txs(self, tx_set):
        with transaction_pool.lock:
            done_transactions.update(tx_set) 
            transaction_pool.transactions -= tx_set

                
        
    
  
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
        except Exception as e:
            print("send transaction from {} to {} faild".
                    format(current_app.config['port'], port))
            print(e)
        
            
class GetChain(MethodView):
    # return whole chain in this node.
    def get(self):
        blockchain = get_blockchain_for_view()
        return jsonify(blockchain), 200
        


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
    app.add_url_rule('/chain', view_func=GetChain.as_view('chain'))
    app.run(host=nodedata.HOST, port=int(port), threaded=True, use_debugger=True)
