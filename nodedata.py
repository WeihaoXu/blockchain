from datatypes import Block, BlockChain, Transaction


HOST = 'localhost'
MAX_TX_PER_BLOCK = 10

blockchain = BlockChain()
pending_transactions = set()
