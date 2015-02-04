from .store import Store


class TokenStore(Store):

    def __init__(self):
        # Use Redis db=3 for tokens
        super(TokenStore, self).__init__(db=3)


token_store = TokenStore()