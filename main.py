import User
from Listener import ThreadListener
from ServerListener import BlockListener
from BlockChain import local_blockchain, Blockchain
import os
import signal
from Crypto.PublicKey import RSA


print("")
print("DDDDDDDDDDDDD           SSSSSSSSSSSSSSS    SSSSSSSSSSSSSSS         CCCCCCCCCCCCC                   iiii  ")
print("D::::::::::::DDD      SS:::::::::::::::S SS:::::::::::::::S     CCC::::::::::::C                  i::::i   ")
print("D:::::::::::::::DD   S:::::SSSSSS::::::SS:::::SSSSSS::::::S   CC:::::::::::::::C                   iiii      ")
print("DDD:::::DDDDD:::::D  S:::::S     SSSSSSSS:::::S     SSSSSSS  C:::::CCCCCCCC::::C                               ")
print("  D:::::D    D:::::D S:::::S            S:::::S             C:::::C       CCCCCC   ooooooooooo   iiiiiiinnnn  nnnnnnnn ")
print("  D:::::D     D:::::DS:::::S            S:::::S            C:::::C               oo:::::::::::oo i:::::in:::nn::::::::nn ")
print("  D:::::D     D:::::D S::::SSSS          S::::SSSS         C:::::C              o:::::::::::::::o i::::in::::::::::::::nn ")
print("  D:::::D     D:::::D  SS::::::SSSSS      SS::::::SSSSS    C:::::C              o:::::ooooo:::::o i::::inn:::::::::::::::n")
print("  D:::::D     D:::::D    SSS::::::::SS      SSS::::::::SS  C:::::C              o::::o     o::::o i::::i  n:::::nnnn:::::n")
print("  D:::::D     D:::::D            S:::::S            S:::::SC:::::C              o::::o     o::::o i::::i  n::::n    n::::n")
print("  D:::::D    D:::::D             S:::::S            S:::::S C:::::C       CCCCCCo::::o     o::::o i::::i  n::::n    n::::n")
print("DDD:::::DDDDD:::::D  SSSSSSS     S:::::SSSSSSSS     S:::::S  C:::::CCCCCCCC::::Co:::::ooooo:::::oi::::::i n::::n    n::::n")
print("  D:::::D     D:::::D       SSSSSS::::S        SSSSSS::::S C:::::C              o::::o     o::::o i::::i  n::::n    n::::n")
print("D:::::::::::::::DD   S::::::SSSSSS:::::SS::::::SSSSSS:::::S   CC:::::::::::::::Co:::::::::::::::oi::::::i n::::n    n::::n")
print("D::::::::::::DDD     S:::::::::::::::SS S:::::::::::::::SS      CCC::::::::::::C oo:::::::::::oo i::::::i n::::n    n::::n")
print("DDDDDDDDDDDDD         SSSSSSSSSSSSSSS    SSSSSSSSSSSSSSS           CCCCCCCCCCCCC   ooooooooooo   iiiiiiii nnnnnn    nnnnnn")
print("")


print("---------------------------------------------------")
print("|                                                 |")
print("| Welcome to DSSCoin, type \'register\' or \'login\': |")
print("|                                                 |")
print("---------------------------------------------------")

# get the user operation
op = input()

if op == "register":
    print("Registration: operation started...")
    # print("DEBUG_LOG: call User.register()")
    public, private = User.register()

else:
    if op == "login":
        print("Insert your private key:")
        key = input()
        User.update_blockchain()
        print("Login operation started...")
        # print("DEBUG_LOG: call User.login()")
        public, private = User.login(key)
        if public is None and private is None:
            print("Login: The key inserted doesn't exist")
            print("Registration: operation started...")
            public, private = User.register()
    else:
        public = private = None
        print("Wrong operation! I'm exiting with error")
        os.kill(os.getpid(), signal.SIGTERM)

# User.send_money(private, public)
print("Checking Blockchain: operation started\n")

if not User.exists_blockchain():
    print("Creating Genesis Block\n")
    # print("DEBUG_LOG: call create_genesis()\n")
    Blockchain.create_genesis(local_blockchain, public)
    # print("DEBUG_LOG: create_genesis() ended")
else:
    print("Synchronizing Blockchain")
    # print("DEBUG_LOG: call update_blockchain()")
    User.update_blockchain()
    # print("DEBUG_LOG: update_blockchain() ended")

print("Checking Blockchain: operation terminated\n")
# print("DEBUG_LOG: start listener thread")

# This thread listen to exists and update requests. This thread also listen to transaction incoming from the network.
listener = ThreadListener()
listener.start()

# This thread listen to blocks mined from other peers.
block_listener = BlockListener()
block_listener.start()

while True:
    # DEBUG - each process prints the hash of the last block (in this case, the genesis block)
    print("\n")
    print("Hash of the current block: ")
    print(local_blockchain.get_last_hash())
    print("\n")
    print("---------------------------------------------------")
    print("|                                                 |")
    print("| Available functions:                            |")
    print("| (insert a number between 1 and 4)               |")
    print("|    1) Send money                                |")
    print("|    2) Show the Blockchain                       |")
    print("|    3) History of transactions                   |")
    print("|    4) Exit                                      |")
    print("|                                                 |")
    print("---------------------------------------------------")

    # get the operation desired
    op = input()
    if op == "":
        continue
    op = int(op)
    if op > 4 or op < 1:  # error
        print("I'm exiting with error")
        os.kill(os.getpid(), signal.SIGTERM)

    elif op == 1:  # send money
        # print("DEBUG_LOG: call send_money()")
        print("Send money started")
        User.send_money(private, public)
        # print("DEBUG_LOG: send_money() ended")

    elif op == 2:  # show the blockchain
        print("Actual Blockchain:")
        local_blockchain.print()

    elif op == 3:  # history of transaction of the user
        print("Transaction History:")
        print("Insert public key:")
        key_input = input()
        public_key = key_input.split("_")
        if key_input != "":
            local_blockchain.print_user_transactions(RSA.construct((int(public_key[0]), int(public_key[1]))))
        else:
            local_blockchain.print_user_transactions(public)

    elif op == 4:  # exit
        print("########### THE END ###########")
        os.kill(os.getpid(), signal.SIGTERM)
