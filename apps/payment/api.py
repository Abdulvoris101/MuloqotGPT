from p2p_payme.client import PaymeClient
import os

phone_number = os.environ.get("PHONE")
password = os.environ.get("PASSWORD_PAYME")
device = os.environ.get("DEVICE")

client = PaymeClient(phone_number, password, device)

card = client.cards.get(name="uzcard")


class Cheque:

    @classmethod
    def get_transaction(cls, comment):
        transaction = client.transactions(card.id).filter(description=comment)

        if len(transaction) == 0 or transaction is None:
            return False
        
        return transaction[0]