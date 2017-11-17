import sys
import hashlib
import json
import flask
from flask import Flask, jsonify, request
from flask.views import MethodView
from datatypes import Block, BlockChain, Transaction
from threading import Lock
import nodedata 
from flask import current_app
import requests



class Mine(MethodView):
    def get(self):
        blockchain, tx_pool = nodedata.blockchain, nodedata.transaction_pool
        txs_to_include = self.select_transaction_set()
        block = blockchain.mine_block(__name__, list(txs_to_include))
        with blockchain.lock:
            if blockchain.validate_new_block(block):
                blockchain.add_block(block)
                self.broadcast_new_block(block)
                with tx_pool.lock:
                    tx_pool.transactions-= txs_to_include
                return jsonify(nodedata.get_blockchain_for_view())
            return "block to add is invalid"

    def select_transaction_set(self):
        selected = set()
        tx_pool = nodedata.transaction_pool
        with tx_pool.lock:
            for tx in tx_pool.transactions:
                selected.add(tx)
                if(len(selected) == nodedata.MAX_TX_PER_BLOCK):
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
        blockchain = nodedata.blockchain
        data = flask.request.data
        data = json.loads(data.decode('utf-8'))
        print(data)
        block = Block.retrive_from_dict(data['block'])
        with blockchain.lock:
            if blockchain.validate_new_block(block):
                blockchain.add_block(block)
        print(blockchain)
        return 'ok', 200
        
    
  
class ReceiveTransaction(MethodView):
    def get(self):
        with nodedata.transaction_pool.lock:
            nodedata.transaction_pool.transactions.add()
            

class ViewChain(MethodView):
    def get(self):
        blockchain = nodedata.get_blockchain_for_view()
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
    app.add_url_rule('/receive', view_func=ReceiveTransaction.as_view('receive'))
    app.add_url_rule('/view', view_func=ViewChain.as_view('view'))
    app.add_url_rule('/receive_block', view_func=ReceiveBlock.as_view('receive_block'))
    app.run(host=nodedata.HOST, port=int(port), threaded=True, use_debugger=True)
