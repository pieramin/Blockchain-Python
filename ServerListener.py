from threading import Thread
import socket
import struct
import User
import json
from Block import Block
from BlockChain import local_blockchain
import hashlib
from Transaction import Transaction


def set_buffer(tmp: str):
    User.buffer = tmp


# this function verified if the proof of work is correct calculating the hash
def validate_proof_of_work(block):
    str_to_hash = ""
    for i in range(0, len(block.transactions)):
        str_to_hash += block.transactions[i].sender + str(block.transactions[i].amount) + \
                       block.transactions[i].receiver + str(block.transactions[i].timestamp)

    str_to_hash += local_blockchain.last_block().block_hash + str(block.nonce) + str(block.timestamp)

    first_hash_256 = hashlib.sha256(str_to_hash.encode()).hexdigest()
    second_hash_256 = hashlib.sha256(first_hash_256.encode()).hexdigest()
    if second_hash_256[:local_blockchain.difficulty] == local_blockchain.difficulty * "0":
        return True
    else:
        return False


# This Thread listen to the answer given by other peers.
class ServerThreadListener(Thread):

    # This method represents the operations of the thread
    def run(self):
        # creation of the socket:  IPv4 of type UDP
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # SO_REUSEADDR  Indicates that the rules used in validating addresses supplied
        #               in a bind call should allow reuse of local addresses
        sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # this bind uses '' that it's the same as INADDR_ANY
        sock1.bind(('', 2001))

        # this function translates the passed values to bytes with specified rules.
        # s = char (4s means 4 byte), l = long, = native byte order + standard size and alignment
        # 224.0.0.0 is a multicast ip.
        mreq1 = struct.pack("=4sl", socket.inet_aton("224.0.0.0"), socket.INADDR_ANY)

        # adds the socket at the multicast group
        sock1.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq1)

        # print("DEBUG_LOG: the thread is listening")
        buffer = sock1.recv(2 ** 16).decode()
        # print("receiver:"+ buffer)
        set_buffer(buffer)
        # print(User.buffer)


# This Thread listen to the blocks just mined to others clients, validate them and adds them to the local blockchain
class BlockListener(Thread):

    def run(self):
        # creation of the socket:  IPv4 of type UDP
        sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # SO_REUSEADDR  Indicates that the rules used in validating addresses supplied
        #               in a bind call should allow reuse of local addresses
        sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # this bind uses '' that it's the same as INADDR_ANY
        sock1.bind(('', 2002))

        # this function translates the passed values to bytes with specified rules.
        # s = char (4s means 4 byte), l = long, = native byte order + standard size and alignment
        # 224.0.0.0 is a multicast ip.
        mreq1 = struct.pack("=4sl", socket.inet_aton("224.0.0.0"), socket.INADDR_ANY)

        # adds the socket at the multicast group
        sock1.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq1)

        # print("DEBUG_LOG: the thread is listening")

        # dual block contains the block that has collapsed with another one of the blockchain.
        # We maintain the block to invalidate the one sent by Eve.
        dual_block = None

        while True:

            buffer = sock1.recv(10240).decode()

            block_received = json.loads(buffer)

            # print("BLOCK LISTENER")
            # print("block listener: " + buffer)
            if buffer == " ":
                print("empty buffer")
                continue

            i_index = block_received['index']
            i_transactions = block_received['transactions']
            i_nonce = block_received['nonce']
            i_previous_hash = block_received['previous_hash']
            i_timestamp = block_received['timestamp']

            transactions = []
            for j in i_transactions:
                tmp = i_transactions[j]
                tmp_sender = tmp['sender']
                tmp_amount = tmp['amount']
                tmp_receiver = tmp['receiver']
                tmp_timestamp = tmp['timestamp']
                tmp_sign = tmp['sign']
                new_transaction = Transaction(tmp_sender, tmp_amount, tmp_receiver, eval(tmp_sign), tmp_timestamp)
                transactions.append(new_transaction)

            if i_transactions["2"]["receiver"] == str(User.public_key.n) + "_" + str(User.public_key.e):
                print("i don't answer to myself")
                continue

            new_block = Block(i_index, transactions, i_nonce, i_previous_hash, i_timestamp)

            if dual_block is not None:
                if dual_block.block_hash == new_block.previous_hash:
                    local_blockchain.remove_tail(new_block.index - 1)
                    local_blockchain.add_block(dual_block)
                    dual_block = None

            print("validate proof of work: " + str(validate_proof_of_work(new_block)))

            block_interested = None

            try:
                block_interested = local_blockchain.get_chain()[new_block.index]
            except IndexError:
                print("the block arrived doesn't exist in the local blockchain, I'm adding it...")
                if validate_proof_of_work(new_block):
                    local_blockchain.add_block(new_block)
                    continue

            if block_interested is not None and new_block.timestamp < block_interested.timestamp:
                local_blockchain.remove_tail(new_block.index)
                print("DEBUG BLOCK LISTENER")
                local_blockchain.add_block(new_block)
                dual_block = block_interested
                continue

            dual_block = new_block
