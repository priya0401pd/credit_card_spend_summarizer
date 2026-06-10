BUSINESS_CONTEXT = """
Business Meaning:

customers
- Customer master information

credit_cards
- Card information
- Contains card variant
- Contains reward point balance

card_transactions
- Transaction history
- amount = transaction spend amount
- txn_date = transaction date

billing_statements
- Monthly statement information

reward_transactions
- Reward point earning and redemption history

Important:
- Spend calculations should use card_transactions.amount
- Date filtering should use card_transactions.txn_date
- Customer card details come from credit_cards

"""