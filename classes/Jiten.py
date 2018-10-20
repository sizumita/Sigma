from bs4 import BeautifulSoup
import requests
import re
import random
url = "https://kokugo.jitenon.jp/cat/gojuon.php?word={}&page=2"


def search_word_from_jiten(word, no_words, t):
    params = {
        'word': word,
        'page': str(random.randint(2, 50))
    }
    r = requests.get(url, params=params)
    r.encoding = r.apparent_encoding
    html = r.text
    soup = BeautifulSoup(html, "html.parser")
    base_data = soup.find_all("a", href=re.compile("https://kokugo\.jitenon\.jp/word/p"))
    l = [i.text for i in base_data if not i.text in no_words and i.text[-2] != "ん" and t.tokenize(i.text)[0].part_of_speech.startswith("名詞,一般")]
    if not l:
        return search_word_from_jiten(word, no_words, t)
    o = random.choice(l)
    return o
