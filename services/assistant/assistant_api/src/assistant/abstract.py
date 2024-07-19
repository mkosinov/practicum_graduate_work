class AbstractAssistant:
    def create_response(self, **kwargs):
        raise NotImplementedError("")

    def get_tokens(self, request):
        raise NotImplementedError("")

    def get_intents(self, request):
        raise NotImplementedError("")

    def get_entities(self, request):
        raise NotImplementedError("")
