import datetime
import hashlib
import json


class Transaction:
    def __init__(self, sender, receiver, value):
        self.sender = sender
        self.receiver = receiver
        self.value = value

    def __str__(self):
        tx_dict = {
            'sender': self.sender,
            'receiver': self.receiver,
            'value': self.value
        }
        return json.dumps(tx_dict, sort_keys=True, indent=4)

    def hash(self):
        tx_str = str(self)
        return hashlib.sha256(tx_str.encode("utf-8")).hexdigest()


class Block:
    TARGET_DIGITS = 3
    MINER_REWARD= 1
    def __init__(self, prev_hash, transactions):
        self.prev_hash = prev_hash
        self.transactions = transactions 
        self.timestamp = str(datetime.datetime.now())
        self.txs_hash = self.transactions_hash()
        self.nonce, self.hashcode = self.proof_of_work()
    
    def __str__(self):
        block_dict = {
            'timestamp': self.timestamp,
            'prev_hash': self.prev_hash,
            'nonce': self.nonce,
            'transactions_hash': self.txs_hash,
            'transactions': [str(tx) for tx in self.transactions],
            'hashcode': self.hashcode
        }
        return json.dumps(block_dict, sort_keys=True, indent=4)


    # attribute account into hash: timestamp, prev_hash, transactions hash, nonce
    def proof_of_work(self):
        nonce = 1
        while True:
            attr_strs = "{}{}{}{}".format(self.timestamp, self.prev_hash, self.txs_hash, nonce)
            hashcode = hashlib.sha256(attr_strs.encode("utf-8")).hexdigest()
            if hashcode[0:self.TARGET_DIGITS] == "0" * self.TARGET_DIGITS:
                return (nonce, hashcode)
            nonce += 1  


    # hash of all transactions in block (can later be replaced with MerkleRoot hash)
    def transactions_hash(self):
        hashcode = hashlib.sha256()
        for tx in self.transactions:
            hashcode.update(tx.hash().encode('utf-8'))
        return hashcode.hexdigest()
            
    @staticmethod
    def new_genesis_block():
        return Block(prev_hash="000", transactions=[])


class BlockChain:
    def __init__(self):
        self.blocks = [Block.new_genesis_block()]

    def add_block(self, transactions):
        prev_block = self.last_block()
        new_block = Block(prev_block.hashcode, transactions)
        self.blocks.append(new_block)

    def last_block(self):
        return self.blocks[-1]

    def __str__(self):
        string = ""
        for block in self.blocks:
            string = string + str(block) + '\n'
        return string

            
    
        


if __name__ == "__main__":
    bc = BlockChain()
    bc.add_block([Transaction('Tom', 'Mike', 20)])
    bc.add_block([Transaction('Mike', 'George', 20)])
    print(bc)

    
    
    
