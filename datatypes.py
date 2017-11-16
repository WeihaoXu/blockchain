import datetime
import hashlib
import json
from threading import Lock


class Transaction:
    MINER_REWARD= 1
    def __init__(self, sender, receiver, value):
        self.sender = sender
        self.receiver = receiver
        self.value = value
        self.hash = self.calculate_hash()

    def to_dict(self):
        tx_dict = {
            'sender': self.sender,
            'receiver': self.receiver,
            'value': self.value
        }
        return tx_dict

    def __str__(self):
        tx_dict = self.to_dict()
        return json.dumps(tx_dict, sort_keys=True, indent=4)

    def calculate_hash(self):
        tx_str = str(self)
        return hashlib.sha256(tx_str.encode("utf-8")).hexdigest()

    @staticmethod
    def reward_transaction(miner):
        return Transaction(None, miner, Transaction.MINER_REWARD)

        



class Block:
    TARGET_DIGITS = 4
    def __init__(self, prev_hash, transactions):
        self.prev_hash = prev_hash
        self.transactions = transactions 
        self.timestamp = str(datetime.datetime.now())
        self.nonce, self.hashcode = self.proof_of_work()
    
    def __str__(self):
        block_dict = self.to_dict()
        return json.dumps(block_dict, sort_keys=True, indent=4)

    def to_dict(self):
        block_dict = {
            'timestamp': self.timestamp,
            'prev_hash': self.prev_hash,
            'nonce': self.nonce,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'hashcode': self.hashcode
        }
        return block_dict
        

        
    # attribute account into hash: timestamp, prev_hash, transactions hash, nonce
    def proof_of_work(self):
        self.nonce = 1
        while True:
            hashcode = self.calculate_hash()
            if hashcode[0:self.TARGET_DIGITS] == "0" * self.TARGET_DIGITS:
                return (self.nonce, hashcode)
            self.nonce += 1  

    def calculate_hash(self):
            txs_hash = self.transactions_hash()
            attr_strs = "{}{}{}{}".format(self.timestamp, self.prev_hash, 
                                            txs_hash, self.nonce)
            hashcode = hashlib.sha256(attr_strs.encode("utf-8")).hexdigest()
            return hashcode

    # hash of all transactions in block (can later be replaced with MerkleRoot hash)
    def transactions_hash(self):
        hashcode = hashlib.sha256()
        for tx in self.transactions:
            hashcode.update(tx.hash.encode('utf-8'))
        return hashcode.hexdigest()
            
    @staticmethod
    def new_genesis_block():
        return Block(prev_hash="000", transactions=set())


class BlockChain:
    def __init__(self):
        self.blocks = [Block.new_genesis_block()]
        self.lock = Lock()

    def mine_block(self, miner, transactions):
        transactions.add(Transaction.reward_transaction(miner)) 
        prev_block = self.last_block()
        new_block = Block(prev_block.hashcode, transactions)
        return new_block

    def add_block(self, mined_block):
        self.blocks.append(mined_block)

    def last_block(self):
        return self.blocks[-1]

    def __str__(self):
        string = ""
        for block in self.blocks:
            string = string + str(block) + '\n'
        return string

    def validate_new_block(self, new_block):
        return BlockChain.validate_block(self.last_block(), new_block)

    @staticmethod
    def validate_block(prev_block, block):
        if not isinstance(block, Block):
            return false
        if not prev_block.hashcode == block.prev_hash:
            return false
        if not block.calculate_hash() == block.hashcode:
            return false
        return True
        

            
    
        


if __name__ == "__main__":
    bc = BlockChain()
    block1 = bc.mine_block('miner1', {Transaction('Tom', 'Mike', 20)})
    bc.add_block(block1)
    block2 = bc.mine_block('miner2', {Transaction('Mike', 'George', 20)})
    bc.add_block(block2)
    print(bc)

    
    
    
