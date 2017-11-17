from datatypes import Block, BlockChain, Transaction, TransactionPool


HOST = 'localhost'
MAX_TX_PER_BLOCK = 10

blockchain = BlockChain()
transaction_pool = TransactionPool() 
done_transactions = set()

def get_blockchain_for_view():
    blockchain_data = {
        'chain': blockchain.to_dict(),
        'length': len(blockchain.blocks)
    }
    return blockchain_data
