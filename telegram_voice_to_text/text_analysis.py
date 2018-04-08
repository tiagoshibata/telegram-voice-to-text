from google.cloud.language import LanguageServiceClient, enums, types

from .state import get_state


def classify(text, verbose=True):
    """Classify the input text into categories."""
    text = _preprocess_text(text)
    if not text:
        return
    language_client = LanguageServiceClient()

    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language=get_state().language)
    try:
        response = language_client.classify_text(document)
    except Exception as e:
        print(e)
        return
    categories = response.categories

    result = {x.name: x.confidence for x in categories}
    print(result)
    return result


def binary_sentiment(text, verbose=True):
    client = LanguageServiceClient()
    # The text to analyze
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language=get_state().language)

    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(document=document).document_sentiment
    if verbose:
        # print('Text: {}'.format(text))
        print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))

    return sentiment.score


def _preprocess_text(raw_text):
    words = len(raw_text.split(sep=' '))
    if words < 10:
         return None
    if words < 20:
        extended_text = raw_text + ' ' + raw_text
        return extended_text
    return raw_text


def process_text(text):
    bin_score = binary_sentiment(text)
    categories_dict = classify(text)
    return bin_score, categories_dict

blacklist = ['fogo', 'emergencia', 'emergência', 'tiro', 'policia', 'morte',
            'incêndio', 'socorro', '911', 'emergency', 'fire', 'urgent']


def is_emergency_text(text):
    return any(word in text.lower() for word in blacklist)


def is_desired_category(text_categories):
    if not text_categories:
        return False
    desired_categories = get_state().filters.text_categories
    text_categories = text_categories.keys()
    print('Checking categories {} against {}'.format(text_categories, desired_categories))
    return any(any(x in category for x in desired_categories) for category in text_categories)
