from datatypes import Block, BlockChain, Transaction, TransactionPool


HOST = 'localhost'
MAX_TX_PER_BLOCK = 10

blockchain = BlockChain()
transaction_pool = TransactionPool() 
done_transactions = set()

def get_blockchain_for_view():
    VIEW_BLOCKS = 4
    idx_high = blockchain.get_length()
    idx_low = max(0, idx_high - VIEW_BLOCKS)
    block_dicts = []
    for i in range(idx_low, idx_high):
        try:
            block_dict = blockchain.blocks[i].to_view_dict()
            block_dict['index'] = i
            block_dict['hashcode'] = block_dict['hashcode'][:10]
            block_dict['prev_hash'] = block_dict['prev_hash'][:10]
            block_dicts.append(block_dict)
        except:
            print("block " + str(i) + " not exist")
    blockchain_data = {
        'blocks': block_dicts,
        'length': len(blockchain.blocks)
    }
    return blockchain_data


def get_blockchain():
    blockchain_data = {
        'chain': blockchain.to_dict(),
        'length': len(blockchain.blocks)
    }
    return blockchain_data
