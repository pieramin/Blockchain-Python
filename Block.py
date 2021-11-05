import hashlib
from time import time
from Transaction import Transaction

# this is a class that represents a block entity in the blockchain structure
class Block:

    def __init__(self, index, transactions:list, nonce, previous_hash, timestamp=time()):
        """
        Creates a block object 
        Parameters:
        - index (int) is the index in tha array
        - transactions (array of Transactions)
        - nonce (int) it needs for the Proof of Work definition
        - previous_hash (str) hash of the previous block in the blockchain
        - timestamp (float) instant of block creation
        """
        self.index = index
        self.transactions = transactions
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.timestamp = timestamp

        string_to_hash = ""
        for i in transactions:
            string_to_hash+=str(i.sender)+str(i.amount)+str(i.receiver)+str(i.timestamp)

        string_to_hash+=str(previous_hash)
        string_to_hash+=str(nonce)
        string_to_hash+=str(timestamp)
        first_hash=hashlib.sha256(string_to_hash.encode()).hexdigest()
        self.block_hash = hashlib.sha256(first_hash.encode()).hexdigest()
