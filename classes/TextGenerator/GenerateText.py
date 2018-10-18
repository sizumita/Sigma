# -*- coding: utf-8 -*-

u"""
マルコフ連鎖を用いて適当な文章を自動生成するファイル
"""

import os.path
import sqlite3
import random
from janome.tokenizer import Tokenizer

if __name__ == '__main__':
    from .PrepareChain import PrepareChain
else:
    from classes.TextGenerator.PrepareChain import PrepareChain


class GenerateText(object):
    u"""
    文章生成用クラス
    """

    def __init__(self, n=5):
        u"""
        初期化メソッド
        @param n いくつの文章を生成するか
        """
        self.n = n
        self.dic_url = "./datas/userdic.csv"
        self.t = Tokenizer(self.dic_url, udic_type="simpledic", udic_enc="utf8")

    def reload(self):
        self.t = Tokenizer(self.dic_url, udic_type="simpledic", udic_enc="utf8")

    def generate(self, content):
        u"""
        実際に生成する
        @return 生成された文章
        """
        # DBが存在しないときは例外をあげる
        if not os.path.exists(PrepareChain.DB_PATH):
            raise IOError("DBファイルが存在しません")

        # DBオープン
        con = sqlite3.connect(PrepareChain.DB_PATH)
        con.row_factory = sqlite3.Row

        # 最終的にできる文章
        generated_text = ""

        # 指定の数だけ作成する
        for i in range(self.n):
            text = self._generate_sentence(con, content)
            generated_text += text

        # DBクローズ
        con.close()

        return generated_text

    def generate_index(self, con):
        # 生成文章のリスト
        morphemes = []

        # はじまりを取得
        first_triplet = self._get_first_triplet(con)
        morphemes.append(first_triplet[1])
        morphemes.append(first_triplet[2])

        # 文章を紡いでいく
        while morphemes[-1] != PrepareChain.END:
            prefix1 = morphemes[-2]
            prefix2 = morphemes[-1]
            triplet = self._get_triplet(con, prefix1, prefix2)
            morphemes.append(triplet[2])

        return morphemes

    def _generate_sentence(self, con, content):
        u"""
        ランダムに一文を生成する
        @param con DBコネクション
        @return 生成された1つの文章
        """
        result = ""
        data = self.t.tokenize(content)
        base_keys = [i.surface for i in data]
        try:
            _keys = [i.surface for i in data if i.part_of_speech.startswith(("動詞", "名詞", "形容動詞", "形容詞"))]
            keys = [u for u in _keys if not u.startswith(( "です", "ます", "だ"))]
        except IndexError:
            keys = [i.surface for i in data if not i.surface in ["?", "？", "。", "、", "！", "!"]]
        for x in range(50):
            morphemes = self.generate_index(con)
            # 連結
            result = "".join([i for i in morphemes[:-1]])
            r = self.t.tokenize(result)
            try:
                _rkeys = [i.surface for i in r if i.part_of_speech.startswith(("動詞", "名詞", "形容動詞", "形容詞"))]
                check = [key for key in _rkeys if key in keys]
                if check:
                    return result
            except IndexError:
                pass
        for x in range(50):
            morphemes = self.generate_index(con)
            # 連結
            result = "".join([i for i in morphemes[:-1]])
            for key in base_keys:
                if key in result:
                    return result

        return result

    def _get_chain_from_DB(self, con, prefixes):
        u"""
        チェーンの情報をDBから取得する
        @param con DBコネクション
        @param prefixes チェーンを取得するprefixの条件 tupleかlist
        @return チェーンの情報の配列
        """
        # ベースとなるSQL
        sql = "select prefix1, prefix2, suffix, freq from chain_freqs where prefix1 = ?"

        # prefixが2つなら条件に加える
        if len(prefixes) == 2:
            sql += " and prefix2 = ?"

        # 結果
        result = []

        # DBから取得
        cursor = con.execute(sql, prefixes)
        for row in cursor:
            result.append(dict(row))

        return result

    def _get_first_triplet(self, con):
        u"""
        文章のはじまりの3つ組をランダムに取得する
        @param con DBコネクション
        @return 文章のはじまりの3つ組のタプル
        """
        # BEGINをprefix1としてチェーンを取得
        prefixes = (PrepareChain.BEGIN,)

        # チェーン情報を取得
        chains = self._get_chain_from_DB(con, prefixes)
        # print(chains)

        # 取得したチェーンから、確率的に1つ選ぶ
        triplet = self._get_probable_triplet(chains)

        return (triplet["prefix1"], triplet["prefix2"], triplet["suffix"])

    def _get_triplet(self, con, prefix1, prefix2):
        u"""
        prefix1とprefix2からsuffixをランダムに取得する
        @param con DBコネクション
        @param prefix1 1つ目のprefix
        @param prefix2 2つ目のprefix
        @return 3つ組のタプル
        """
        # BEGINをprefix1としてチェーンを取得
        prefixes = (prefix1, prefix2)

        # チェーン情報を取得
        chains = self._get_chain_from_DB(con, prefixes)

        # 取得したチェーンから、確率的に1つ選ぶ
        triplet = self._get_probable_triplet(chains)

        return (triplet["prefix1"], triplet["prefix2"], triplet["suffix"])

    def _get_probable_triplet(self, chains):
        u"""
        チェーンの配列の中から確率的に1つを返す
        @param chains チェーンの配列
        @return 確率的に選んだ3つ組
        """
        # 確率配列
        probability = []

        # 確率に合うように、インデックスを入れる
        for (index, chain) in enumerate(chains):
            for j in range(chain["freq"]):
                probability.append(index)

        # ランダムに1つを選ぶ
        # print(probability)
        chain_index = random.choice(probability)

        return chains[chain_index]


if __name__ == '__main__':
    generator = GenerateText()
    print(generator.generate("a"))



