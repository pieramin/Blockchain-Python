import time


class Transaction:

    def __init__(self, sender, amount, receiver, sign, timestamp=time.time()):
        """
        Creates a transaction object
        Parameters:
        - sender (str) è l'account del mittente
        - amount (int) è l'ammontare da trasferire
        - receiver (str) è l'account del destinatario
        - timestamp (float)
        - sign (bytes) sign of the hashed message with the user private key
        """
        self.sender = sender
        self.amount = amount
        self.receiver = receiver
        self.timestamp = timestamp
        self.sign = sign

    # checks if a transaction is valid
    # other checks are made in other files 
    def validate(self):
        if int(self.amount) < 0:
            return False
        return True
