from datatypes import Block, BlockChain, Transaction, TransactionPool


HOST = 'localhost'
MAX_TX_PER_BLOCK = 10

blockchain = BlockChain()
transaction_pool = TransactionPool() 
done_transactions = set()

def get_blockchain_for_view():
    chain_len = len(blockchain.blocks) 

    blockchain_data = {
        'blocks': [block.to_dict() for block in blockchain.blocks[-5:]],
        'length': len(blockchain.blocks)
    }
    return blockchain_data


def get_blockchain():
    blockchain_data = {
        'chain': blockchain.to_dict(),
        'length': len(blockchain.blocks)
    }
    return blockchain_data
