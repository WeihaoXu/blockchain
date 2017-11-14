import datetime
import hashlib
import json



class Block:
    TARGET_DIGITS = 3
    def __init__(self, prev_hash, data, timestamp=None, nonce=None, hashcode = None):
        self.prev_hash = prev_hash
        self.data = data
        if nonce is None and hashcode is None and timestamp is None:
            self.timestamp = str(datetime.datetime.now())
            self.nonce, self.hashcode = self.proof_of_work()
        else:
            self.timestamp, self.nonce, self.hashcode = timestamp, nonce, hashcode


    
    def __str__(self):
        block_dict = {
            'timestamp': self.timestamp,
            'prev_hash': self.prev_hash,
            'nonce': self.nonce,
            'data': self.data,
            'hashcode': self.hashcode
        }
        return json.dumps(block_dict, sort_keys=True, indent=4)

    def proof_of_work(self):
        nonce = 1
        while True:
            attr_strs = "{}{}{}{}".format(self.timestamp, self.prev_hash, self.data, nonce)
            hashcode = hashlib.sha256(attr_strs.encode("utf-8")).hexdigest()
            if hashcode[0:self.TARGET_DIGITS] == "0" * self.TARGET_DIGITS:
                return (nonce, hashcode)
            nonce += 1  

    def serialize(self):
        return str(self) 

    @staticmethod
    def deserialize(string):
        block_dict = json.loads(string)
        return Block(block_dict['prev_hash'], block_dict['data'], block_dict['timestamp'],
                        block_dict['nonce'], block_dict['hashcode'])

    @staticmethod
    def new_genesis_block():
        return Block(prev_hash="000", data=None)

        
        


class BlockChain:
    def __init__(self, blocks=None):
        if blocks is None:
            self.blocks = [Block.new_genesis_block()]
        else:
            self.blocks = blocks

    def add_block(self, data):
        prev_block = self.last_block()
        new_block = Block(prev_block.hashcode, data)
        self.blocks.append(new_block)

    def last_block(self):
        return self.blocks[-1]

    def __str__(self):
        blockchain_dict = {
            'blocks': [block.serialize() for block in self.blocks]
        }
        return json.dumps(blockchain_dict, sort_keys=True, indent=4)

    def serialize(self):
        return str(self)
        
    @staticmethod
    def deserialize(string):
        blocks = []
        blockchain_str = json.loads(string)
        for block_str in blockchain_str['blocks']:
            blocks.append(Block.deserialize(block_str))
        return BlockChain(blocks)
            
    
        


if __name__ == "__main__":
    bc = BlockChain()
    bc.add_block("hello") 
    bc.add_block("how are you")
    #print(bc.last_block().serialize())
    block_str = bc.last_block().serialize()
    print("serialize/deserialize of last block:")
    print(block_str)
    print(Block.deserialize(block_str))
    print("serialize/deserialize whole chain:")
    bc_str = bc.serialize()
    print(bc_str)
    print(BlockChain.deserialize(bc_str))
    
    
    
