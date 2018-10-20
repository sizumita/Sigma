import requests
search_word_url = "https://ja.wikipedia.org/w/api.php"


def search_word(word):
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': word,
        'format': 'json'
    }
    r = requests.get(search_word_url, params=params)
    json = r.json()
    if json['query']['searchinfo']['totalhits'] == 0:
        return False
    return json

