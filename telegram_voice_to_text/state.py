class Filter:
    speech_sentiments_enabled = False
    text_categories = []
    enable_get_categories = False

class BotState:
    language = 'en-US'
    filters = Filter()


_state = None


def get_state():
    global _state
    if not _state:
        _state = BotState()
    return _state
