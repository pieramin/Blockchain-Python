import hashlib
from time import time
from Block import Block
from Transaction import Transaction
from Crypto.PublicKey import RSA


class Blockchain:
    # number of zero for the Proof of Work
    difficulty = 2
    # data for the genesis block, like in Bitcoin
    initial_hash = "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks"
    TRANSACTION_IN_BLOCK = 3

    def __init__(self):
        # transaction not already mined
        self.__current_transactions = []
        # Blockchain
        self.__chain = []

    # function that creates the first block in the blockchain
    def create_genesis(self, public_key: RSA.RsaKey):
        genesis_block_transactions = self.__current_transactions
        # print("DEBUG_LOG: call function mine() inside create_genesis()")
        self.mine(public_key, genesis_block_transactions)
        # print("DEBUG_LOG: mine() inside create_genesis() terminated")

    # if it's valid, this function appends a block at the end of the blockchain
    def add_block(self, block):
        if self.validate_block(block, self.last_block()):
            self.__chain.append(block)
            self.__current_transactions = []
            return True
        return False

    # # # # # # # # # # # # utilities # # # # # # # # # # # #

    # get the last block in the blockchain, if exists
    def last_block(self):
        if not self.__chain:
            return []
        return self.__chain[-1]

    # get the last transaction not already mined
    def last_transaction(self):
        return self.__current_transactions[-1]

    # get the transactions not already mined
    def pending_transactions(self):
        return self.__current_transactions

    # this function returns the entire blockchain
    def get_chain(self):
        return self.__chain

    # this function returns the hash of the last block mined
    def get_last_hash(self):
        return self.__chain[-1].block_hash

    # this function removes all the blocks from index to the end of the blockchain
    def remove_tail(self, index):
        self.__chain = self.__chain[0:index]

    # creates a transaction and put it in the __current_transaction list
    def create_transaction(self, sender, amount, receiver, sign, timestamp=time()):

        transaction = Transaction(sender, amount, receiver, sign, timestamp)

        if transaction.validate():
            self.__current_transactions.append(transaction)
            return transaction, True
        return None, False

    # this function builds the reward transaction for the miner and try to generate
    # a valid proof of work, then add the new block mined to the blockchain
    def mine(self, reward_address: RSA.RsaKey, new_block_transactions):
        last_block = self.last_block()

        if not last_block:
            previous_hash = self.initial_hash
            index = 0
        else:
            index = last_block.index + 1
            previous_hash = last_block.block_hash

        # reward transaction amount = 50 DSSCoin, this transaction dosen't have a sender
        self.create_transaction(sender="0", amount=50, receiver=str(reward_address.n) + "_" + str(reward_address.e),
                                sign=b"reward")

        # mining definition is applied in this function called
        # print("DEBUG_LOG: chiamata a generate_proof_of_work() dentro a mine()")
        nonce, timestamp = self.generate_proof_of_work(new_block_transactions)
        # print("DEBUG_LOG: generate_proof_of_work() dentro a mine() terminata

        block = Block(index, self.__current_transactions, nonce, previous_hash, timestamp)

        if self.add_block(block):
            return block

        return None

    # looks for a value (nonce) that, concatenated with the data in a block,
    # makes a hash with self.difficulty zeros ahead
    def generate_proof_of_work(self, block_transactions):

        number = 0  # for the style of the output
        nonce = 0

        print("Attempts: ")
        while True:
            # concatenation of the parameters on which to calculate the hash
            if not local_blockchain.last_block():
                string_to_hash = ""

                for i in range(0, len(self.__current_transactions)):
                    string_to_hash += block_transactions[i].sender + str(block_transactions[i].amount) + \
                                      block_transactions[i].receiver + str(block_transactions[i].timestamp)

                string_to_hash += self.initial_hash + str(nonce)


            else:
                string_to_hash = ""

                for i in range(0, len(self.__current_transactions)):
                    string_to_hash += block_transactions[i].sender + str(block_transactions[i].amount) + \
                                      block_transactions[i].receiver + str(block_transactions[i].timestamp)

                string_to_hash += local_blockchain.last_block().block_hash + str(nonce)

            # double hash as in Bitcoin protocol
            timestamp = time()
            string_to_hash += str(timestamp)

            first_hash_256 = hashlib.sha256(string_to_hash.encode()).hexdigest()
            second_hash_256 = hashlib.sha256(first_hash_256.encode()).hexdigest()

            # output
            print(str(number) + ": " + second_hash_256)

            # Proof of Work definition
            if second_hash_256[:Blockchain.difficulty] == "0" * Blockchain.difficulty:
                print("")
                return nonce, timestamp

            number += 1
            nonce += 1

    # this function checks if the block received has consistency with the
    # informations owned by the client
    def validate_block(self, current_block, previous_block: list):
        if not previous_block and current_block.index == 0:
            return True

        elif current_block.index != previous_block.index + 1:
            print(current_block.index)
            print(previous_block.index)
            return False

        if current_block.previous_hash != previous_block.block_hash:
            return False

        string_to_hash = ""
        for i in current_block.transactions:
            string_to_hash += str(i.sender) + str(i.amount) + str(i.receiver) + str(i.timestamp)

        string_to_hash += str(self.last_block().block_hash)
        string_to_hash += str(current_block.nonce)
        string_to_hash += str(current_block.timestamp)
        first_hash = hashlib.sha256(string_to_hash.encode()).hexdigest()
        second_hash = hashlib.sha256(first_hash.encode()).hexdigest()

        if current_block.block_hash != second_hash:
            return False

        # check transactions
        if len(current_block.transactions) != self.TRANSACTION_IN_BLOCK:
            return False

        n=0
        for i in current_block.transactions:
            if i.sender==str(0):
                continue
            key=i.sender
            key=key.split("_")
            rsa_key=RSA.construct((int(key[0]), int(key[1])))
            result = self.check_money(rsa_key, current_block.transactions, i)
            n+=1
            if not result:
                return False
        return True

    # check the validity of the transaction amount, leaving out the transaction to be checked
    def check_money(self, public_key: RSA.RsaKey, transactions, transaction):
        amount = 0
        for i in self.__chain:
            for j in i.transactions:
                if j.receiver == str(public_key.n) + "_" + str(public_key.e):
                    amount += int(j.amount)
                if j.sender == str(public_key.n) + "_" + str(public_key.e):
                    amount -= int(j.amount)

        for j in transactions:
            if j==transaction:
                continue

            if j.receiver == str(public_key.n) + "_" + str(public_key.e):
                amount += int(j.amount)
            if j.sender == str(public_key.n) + "_" + str(public_key.e):
                amount -= int(j.amount)
        if amount >= int(transaction.amount):
            return True
        return False

    # it verifies the wallet availability of the client and returns this value
    def count_money(self, public_key: RSA.RsaKey):
        amount = 0

        for i in self.__chain:
            for j in i.transactions:
                if j.receiver == str(public_key.n) + "_" + str(public_key.e):
                    amount += int(j.amount)
                if j.sender == str(public_key.n) + "_" + str(public_key.e):
                    amount -= int(j.amount)

        # print("DEBUG_COUNT MONEY"+str(amount))
        for i in self.__current_transactions:
            if i.receiver == str(public_key.n) + "_" + str(public_key.e):
                amount += int(i.amount)
            if i.sender == str(public_key.n) + "_" + str(public_key.e):
                amount -= int(i.amount)
        # print("DEBUG_COUNT MONEY"+str(amount))

        return amount

    # prints a representation of the current blockchain
    def print(self):

        max_len = len("# Previous hash of the block: " + str(self.initial_hash) + "  ")

        for i in self.__chain:
            info_to_be_printed = []
            info_to_be_printed.append("# Index of the block: " + str(i.index))
            info_to_be_printed.append("# Nonce of the block: " + str(i.nonce))

            if i == local_blockchain.__chain[0]:
                info_to_be_printed.append("# Previous hash of the block: " + str(i.previous_hash))
            else:
                info_to_be_printed.append("# Previous hash of the block: " + str(i.previous_hash)[:64] + "...")

            info_to_be_printed.append("# Timestamp of the block: " + str(i.timestamp))

            # prints sharps
            print(max_len * "#")
            # prints the block i
            print(info_to_be_printed[0] + (max_len - len(info_to_be_printed[0]) - 1) * " " + "#")

            for j in i.transactions:
                print("#      " + "-" * (max_len - 9) + " #")
                transactions_to_be_printed = []

                if int(j.sender) == 0:
                    transactions_to_be_printed.append("#      Sender: " + str(j.sender))
                else:
                    transactions_to_be_printed.append("#      Sender: " + str(j.sender)[:64] + "...")

                transactions_to_be_printed.append("#      Amount: " + str(j.amount))
                transactions_to_be_printed.append("#      Receiver: " + str(j.receiver)[:64] + "...")
                transactions_to_be_printed.append("#      Timestamp: " + str(j.timestamp))

                if int(j.sender) == 0:
                    transactions_to_be_printed.append("#      Sign: " + str(j.sign))
                else:
                    transactions_to_be_printed.append("#      Sign: " + str(j.sign)[:20] + "...")

                # sender
                print(transactions_to_be_printed[0] + (max_len - len(transactions_to_be_printed[0]) - 1) * " " + "#")
                # amount
                print(transactions_to_be_printed[1] + (max_len - len(transactions_to_be_printed[1]) - 1) * " " + "#")
                # receiver
                print(transactions_to_be_printed[2] + (max_len - len(transactions_to_be_printed[2]) - 1) * " " + "#")
                # timestamp
                print(transactions_to_be_printed[3] + (max_len - len(transactions_to_be_printed[3]) - 1) * " " + "#")
                # sign
                print(transactions_to_be_printed[4] + (max_len - len(transactions_to_be_printed[4]) - 1) * " " + "#")

            print("#      " + "-" * (max_len - 9) + " #")
            # prints the nonce of the block
            print(info_to_be_printed[1] + (max_len - len(info_to_be_printed[1]) - 1) * " " + "#")
            # printf the previous hash of the block
            print(info_to_be_printed[2] + (max_len - len(info_to_be_printed[2]) - 1) * " " + "#")
            # prints the hash of the block
            print(info_to_be_printed[3] + (max_len - len(info_to_be_printed[3]) - 1) * " " + "#")
            # printf sharps
            print(max_len * "#")

            if i != local_blockchain.last_block():
                print(int(max_len / 2) * " " + "|")
                print(int(max_len / 2) * " " + "|")
                print(int(max_len / 2) * " " + "|")
                print(int(max_len / 2) * " " + "|")
                print(int(max_len / 2) * " " + "|")
                print(int(max_len / 2 - 1) * " " + "\\" + "|" + "/")
                print(int(max_len / 2) * " " + "V")
            else:
                print("Blockchain Ended")

    # this function prints the history of the user (with address 'public') transactions
    def print_user_transactions(self, public):
        public_key = str(public.n) + "_" + str(public.e)
        index = 1
        current_moneys = 0

        for i in self.__chain:
            for j in i.transactions:
                if j.sender == public_key:
                    print("Transaction no. " + str(index) + ".")
                    print(" Sender: myself")
                    print(" Amount: " + str(j.amount))
                    print(" Receiver: " + j.receiver[:20] + "...")
                    current_moneys -= int(j.amount)
                    index = index + 1

                if j.receiver == public_key:
                    print("Transaction no. " + str(index) + ".")

                    if j.sender != str(0):
                        print(" Sender: " + j.sender[:20] + "...")
                    else:
                        print(" Sender: " + j.sender)
                    print(" Amount: " + str(j.amount))
                    print(" Receiver: myself")
                    current_moneys += int(j.amount)
                    index = index + 1

        print("Current money: " + str(current_moneys))

    # check if a public key is consistent with the data in the blockchain
    def exists_user(self, public):
        public_str = str(public.n) + "_" + str(public.e)

        for i in self.__chain:
            for j in i.transactions:
                if j.receiver == public_str or j.sender == public_str:
                    return True
        return False


# # # # # # # # # # # # #  Blockchain Creation # # # # # # # # # # # # #

local_blockchain = Blockchain()
