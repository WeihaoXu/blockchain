import datetime
import hashlib



class Block:
    TARGET_DIGITS = 3
    def __init__(self, prev_hash, data):
        self.timestamp = datetime.datetime.now()
        self.prev_hash = prev_hash
        self.data = data
        self.nonce, self.hashcode = self.proof_of_work()
    
    def __str__(self):
        string = """
            Timestamp: {}
            Prev.hash: {}
            nonce: {}
            Data: {}
            Hash: {}
        """.format(self.timestamp, self.prev_hash, self.nonce, self.data, self.hashcode)
        return string

    def proof_of_work(self):
        nonce = 1
        while True:
            attr_strs = "{}{}{}{}".format(self.timestamp, self.prev_hash, self.data, nonce)
            hashcode = hashlib.sha256(attr_strs.encode("utf-8")).hexdigest()
            if hashcode[0:self.TARGET_DIGITS] == "0" * self.TARGET_DIGITS:
                return (nonce, hashcode)
            nonce += 1  

    @staticmethod
    def new_genesis_block():
        return Block(prev_hash="000", data=None)

    





class BlockChain:
    def __init__(self):
        self.blocks = [Block.new_genesis_block()]

    def add_block(self, data):
        prev_block = self.last_block()
        new_block = Block(prev_block.hashcode, data)
        self.blocks.append(new_block)

    def last_block(self):
        return self.blocks[-1]

    def __str__(self):
        string = ""
        for i in range(len(self.blocks)):
            string = string + "block {}: {}\n".format(i, self.blocks[i])
        return string


if __name__ == "__main__":
    bc = BlockChain()
    bc.add_block("hello") 
    bc.add_block("how are you")
    print(bc)
    
        
        
        
        
    
    
