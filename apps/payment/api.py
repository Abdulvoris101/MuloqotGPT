# from p2p_payme.client import PaymeClient
# from utils import constants

# phone_number = constants.PHONE
# password = constants.PASSWORD_PAYME
# device = constants.DEVICE

# client = PaymeClient(phone_number, password, device)

# card = client.cards.get(name="uzcard")  


# class Cheque:

#     @classmethod
#     def get_transaction(cls, comment):
#         transaction = client.transactions(card.id).filter(description=comment)

#         if len(transaction) == 0 or transaction is None:
#             return False
        
#         return transaction[0]