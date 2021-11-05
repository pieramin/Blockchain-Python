from threading import Thread
import socket
import struct
from Crypto.PublicKey import RSA
import User
import json
import BlockChain
from BlockChain import local_blockchain

# number of transaction that are necessary to mine the new block
TRANSACTION_IN_BLOCK = 2


# this Thread is listening on port 2000 to incoming requests. Requests can be:
#  -exist blockchain:   This operation answers the question of whether a blockchain exists with yes or no.
#  -update blockchain:  This operation answers the question of whether a blockchain should be updated.
#                       The answer is composed by the missing blocks or an "already uo to date message".
#  -get transaction     This operation get the incoming transaction and check its validity with the sign of the
#                       transaction and the public key

class ThreadListener(Thread):

    # This method represents the operations of the thread
    def run(self):
        # creation of the socket:  IPv4 of type UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        # SO_REUSEADDR  Indicates that the rules used in validating addresses supplied
        #               in a bind call should allow reuse of local addresses
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock1.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        # this bind uses '' that it's the same as INADDR_ANY
        sock.bind(('', 2000))

        # this function translates the passed values to bytes with specified rules.
        # s = char (4s means 4 byte), l = long, = native byte order + standard size and alignment
        # 224.0.0.0 is a multicast ip.
        mreq = struct.pack("=4sl", socket.inet_aton("224.0.0.0"), socket.INADDR_ANY)

        # adds the socket at the multicast group
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # this value counts the pending transactions. when this value is equal to
        # TRANSACTION_IN_BLOCK the block is mined
        transaction_count = 0

        # This function answers to exists requests.
        def exists():
            if not local_blockchain.get_chain():
                sock1.sendto("False".encode(), ("224.0.0.0", 2001))

            if local_blockchain.get_chain():
                sock1.sendto("True".encode(), ("224.0.0.0", 2001))

        # Utility function to send a list of blocks in json format
        # @Input Ini is the initial index of the blockchain to be send
        #        Index is the final index of the blockchain to be send
        # @Requires Ini and Index must be integer

        def send_json(ini, index):
            packets = []
            for i in range(0, index + 1):
                new_block = local_blockchain.get_chain()[i]
                # print("DEBUG_LOG"+ str(new_block.index))
                transactions = new_block.transactions
                # print(transactions)
                dict_tra = []
                for j in range(0, len(transactions)):
                    new_dict = {
                        "sender": transactions[j].sender,
                        "amount": transactions[j].amount,
                        "receiver": transactions[j].receiver,
                        "timestamp": transactions[j].timestamp,
                        "sign": f"{transactions[j].sign}"
                    }
                    dict_tra.append(new_dict)

                # print(dict_tra)
                dict_transactions = {k: dict_tra[k] for k in range(0, len(transactions))}

                new_packet = {
                    "index": new_block.index,
                    "transactions": dict_transactions,
                    "nonce": new_block.nonce,
                    "previous_hash": new_block.previous_hash,
                    "timestamp": new_block.timestamp
                }

                packets.append(new_packet)
            if ini == 0:
                dictionary = {i: packets[i] for i in range(0, index + 1)}
            else:
                dictionary = {i: packets[i] for i in range(ini + 1, index + 1)}

            json_packet = json.dumps(dictionary)
            sock1.sendto(json_packet.encode(), ("224.0.0.0", 2001))
            # fine for su i

        # This function answers to update requests
        def update():
            tmp = receive.decode().split(" ")
            last_block = tmp[1]
            received_public_key = tmp[2]
            if received_public_key != 0:
                if received_public_key == str(User.public_key.n) + "_" + str(User.public_key.e):
                    # print("i don't answer to myself")
                    return
                # in this case the peer that's request the update has an empty blockchain
                if last_block == "empty":
                    index = BlockChain.local_blockchain.last_block().index
                    send_json(0, index)

                # in this case the thread answers "already up to date"
                elif int(last_block) == BlockChain.local_blockchain.last_block().index:
                    # print("DEBUG last block:" + last_block)
                    # print("DEBUG local_blockchain.lastblock"+str(BlockChain.local_blockchain.last_block().index))
                    sock1.sendto("Already up to date".encode(), ("224.0.0.0", 2001))

                # in this case the thread send a partial update.
                elif int(last_block) < BlockChain.local_blockchain.last_block().index:
                    index = BlockChain.local_blockchain.last_block().index
                    send_json(int(last_block), index)

                # In this case we manage invalid index
                elif int(last_block) > BlockChain.local_blockchain.last_block().index:
                    # print("Index not valid")
                    sock1.sendto("index_error".encode(), ("224.0.0.0", 2001))
            else:
                # case login
                index = BlockChain.local_blockchain.last_block().index
                send_json(0, index)

        # if the function receives a transaction and the transaction is valid, the function
        # appends  it to  Blockchain.__current_transactions.
        # When len(Blockchain.__current_transaction) is equal to TRANSACTION_IN_BLOCK,
        # the function mine the new block and send it in multicast.
        def handle_transaction(number_of_transactions):
            message_arrived = receive

            message = json.loads(message_arrived.decode())

            # get the subfields
            message_sender_n = message["sender_n"]
            message_sender_e = message["sender_e"]
            message_amount = message["amount"]
            message_receiver_n = message["receiver_n"]
            message_receiver_e = message["receiver_e"]
            message_timestamp = message["timestamp"]
            message_sign = eval(message["sign"])
            # print(message_sign)
            # print(type(message_sign))
            message.pop("sign")  # pop the sign to check the validity of message
            key_received = str(message_sender_n) + "_" + str(message_sender_e)
            local_private_key = str(User.public_key.n) + "_" + str(User.public_key.e)

            if key_received == local_private_key:
                # return, i don't answer to myself
                local_blockchain.create_transaction(key_received, message_amount,
                                                    str(message_receiver_n) + "_" + str(message_receiver_e),
                                                    message_timestamp)
                # print("DEBUG_LOG: the listener thread has received a local transaction")
                return number_of_transactions

            sender_key = RSA.construct((message_sender_n, message_sender_e))
            User.verify(message.__str__().encode(), message_sign, sender_key)
            # print("Transaction is valid:" + str(is_valid))

            number_of_transactions = number_of_transactions + 1
            local_blockchain.create_transaction(str(message_sender_n) + "_" + str(message_sender_e), message_amount,
                                                str(message_receiver_n) + "_" + str(message_receiver_e), message_sign,
                                                message_timestamp)  # message sign already evaluated

            # start the mine of the block if the number of available transaction is equal to TRANSACTION_IN_BLOCK.
            if number_of_transactions == TRANSACTION_IN_BLOCK:

                number_of_transactions = 0  # set the counter to zero
                block_mined = local_blockchain.mine(User.public_key, local_blockchain.pending_transactions())

                print("Block_mined: ")
                print(block_mined)

                if block_mined is not None:
                    print("MINE: I'm sending the block just mined!")
                    transactions = block_mined.transactions
                    # print(transactions)
                    dict_tra = []
                    for j in range(0, len(transactions)):
                        new_dict = {
                            "sender": transactions[j].sender,
                            "amount": transactions[j].amount,
                            "receiver": transactions[j].receiver,
                            "timestamp": transactions[j].timestamp,
                            "sign": f"{transactions[j].sign}"
                        }

                        dict_tra.append(new_dict)
                    dict_transactions = {k: dict_tra[k] for k in range(0, len(transactions))}
                    new_packet = {
                        "index": block_mined.index,
                        "transactions": dict_transactions,
                        "nonce": block_mined.nonce,
                        "previous_hash": block_mined.previous_hash,
                        "timestamp": block_mined.timestamp,

                    }
                    json_block = json.dumps(new_packet)

                    # print("packet sent"+json_block)
                    sock1.sendto(json_block.encode(), ("224.0.0.0", 2002))
            return number_of_transactions

        # # # # # # # # # # # # main while of the run function # # # # # # # # # # #
        while True:
            # print("DEBUG_LOG: thread is listening...")
            receive = sock.recv(10240)

            msg = " "
            try:
                msg = receive.decode()
            except UnicodeDecodeError:
                print(msg)

            # exists request
            if msg == "exists":
                exists()

            # update request
            elif msg[:6] == "update":
                update()

            # received transaction
            else:
                transaction_count = handle_transaction(transaction_count)
