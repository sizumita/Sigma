from janome.tokenizer import Tokenizer
import discord
import datetime
import re
from classes.decos import owner_only
from classes.baseworker import BaseWorker
import asyncio
import pickle
import random
import aiofiles
from classes.TextGenerator.PrepareChain import PrepareChain
from classes.TextGenerator.GenerateText import GenerateText
from classes.Wikipedia import search_word
from pykakasi import kakasi
from classes.Jiten import search_word_from_jiten
owner = None
help_message = """
```
すみどらちゃん v1.0.2

こんにちは、すみどらちゃんだよ！discordをより良くするように頑張るので、よろしくですっ！
すみどらちゃんって呼びかけてくれたら、反応します！よろしくです！

commands:

!trend サーバー内の1日のトレンドが見れます。

!しりとり しりとりをします

```
"""
what_to_do = """
すみどらちゃんって呼びかけてくれたら反応するよ！

```
何が出来る？って言ってくれればこれを言うよ！

ニュース見せてって言ったらニュースを見せてあげる！

おみくじって言ってくれればおみくじを引くよ！

[ユーザーが言う言葉](って|と)言ったら[私に言って欲しい言葉](って|と)言って　って言ってくれたら覚えるよ！

このチャンネルで挨拶してって言ったら新しい人に挨拶するようになるよ！

ニックネームを覚えてっていったら他の鯖に入ったときにニックネームを自動的に変えてあげる！

しりとりって言ったらしりとりするよ！
```
"""
omi = {
    "大吉": ["今日はいいことがいっぱいあるかも！", "お金拾っちゃったりして？！", "告白すれば必ず叶うよ！"],
    "中吉": ["今日はいい日になりそう！", "お手伝いすればお金がもらえるかも！", "星に願いを！"],
    "小吉": ["今日はちょっぴりいいことがあるかも！", "たくさんの人からお礼を言われるかも！", "お参りしてみよう！"],
    "吉": ["今日は少しいい日かも！", "好きな人からお礼を言われるよ！", "五円のお賽銭をしてみよう！"],
    "末吉": ["今日は願いが叶うかも！", "好きな人に話しかけられるかも！", "北枕で寝てみよう！"],
    "凶": ["今日はちょっぴり付いてない日かも...", "お金落としそうだから気をつけて..", "北枕で寝ないように！"],
    "大凶": ["今日はついてないよ..", "好きな人に嫌われるかも...", "人に媚は使わないように..."],
}
hello = [
    "あっ！{user.name}さんだ！よろしく！",
    "{user.name}さん、このサーバーを楽しんでいってね！",
    "あのねあのね、{user.name}さんを連れてきたよ！",
    "ここに伝説の剣士、{user.name}さんがいる！",
]
what_do_say = re.compile(r"^(.+)(って|と)(言ったら|いったら)(.+)(って|と)(言って|いって).*$")
cannnot_words = [
    "ファシスト",
    "ファシズム",
    "卍",
    "ナチス",
    "ヒトラー",
    "w",
    "sex",
    "セックス",
    "オナニー",
    "ｗ",
    "＠",
    "@",
    "淫夢",
    "(便乗)",
    "（便乗）",
    "バカ",
    "馬鹿",
    "死ね",
    "野獣先輩",
    "迫真",
    "ンアッー!",
    "114",
    "514",
    "1919",
    "やりますね",
]


async def omikuzi(message: discord.Message):
    key = random.choice(list(omi.keys()))
    kekka = random.choice(omi[key])
    channel = message.channel
    await channel.send("おみくじを引くよ...少し待ってて...")
    await channel.send(f"結果は...\n{key}だって！{kekka}\n今日も1日がんばろう！")


class Worker(BaseWorker):
    def __init__(self, client: discord.Client):
        super().__init__(client)
        global owner
        owner = client.get_user(212513828641046529)
        self.dic_url = "./datas/userdic.csv"
        self.t = Tokenizer(self.dic_url, udic_type="simpledic", udic_enc="utf8")
        self.say_b_a = {}
        self.hello_channel_ids = {}
        self.user_nick = {}
        self.generator = GenerateText(n=8)
        self.log_channel = None
        self.not_rlearn_channel = []
        self.is_shiritori = []
        self.kakasi = kakasi()
        self.kakasi.setMode("J", "H")
        self.kakasi.setMode("K", "H")
        self.conv = self.kakasi.getConverter()
        self.wadai = ""
        client.loop.create_task(self.load())

    async def join(self, message: discord.Message):
        await message.channel.send(help_message)
        return True

    async def load(self):
        self.log_channel = self.client.get_channel(502394237589913600)
        try:
            async with aiofiles.open('./datas/say.pickle', 'rb') as f:
                self.say_b_a = pickle.loads(await f.read())
        except (FileNotFoundError, EOFError):
            print(-1)
        try:
            async with aiofiles.open('./datas/hello.pickle', 'rb') as f:
                self.hello_channel_ids = pickle.loads(await f.read())
        except (FileNotFoundError, EOFError):
            print(-1)
        try:
            async with aiofiles.open('./datas/nick.pickle', 'rb') as f:
                self.hello_channel_ids = pickle.loads(await f.read())
        except (FileNotFoundError, EOFError):
            print(-1)

    @owner_only
    async def get_data(self, message: discord.Message):
        data = "```\nkey : value # say_b_a\n"
        for key, value in self.say_b_a.items():
            data += f"{key} : {value}\n"
        data += "```"
        await message.author.send(data)
        data = "key : value #hello"
        for key, value in self.hello_channel_ids.items():
            data += f"{self.client.get_guild(key).name} : {self.client.get_channel(value).name}\n"
        data += "```"
        await message.author.send(data)
        data = "key : value #nick"
        for key, value in self.say_b_a.items():
            data += f"{key} : {value}\n"
        data += "```"
        await message.author.send(data)
        return True

    @owner_only
    async def reload(self, message: discord.Message):
        await message.channel.send("リロードします")
        self.t = Tokenizer(self.dic_url, udic_type="simpledic", udic_enc="utf8")
        await message.channel.send("リロードしました")

    async def trend(self, message: discord.Message):
        if message.content.startswith("!trend set"):
            await self.dicset(message)
            return True
        old_now = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        now = int(old_now.timestamp())
        msg_channel = message.channel
        await msg_channel.send("このサーバー~~ですか？全体ですか？~~って言ってください！")

        def check(m):
            return m.content in ["このサーバー", "全体"] and m.channel == msg_channel and m.author == message.author

        msg = await self.client.wait_for('message', check=check)
        counter = []
        solt = []
        if msg.content == "このサーバー":
            for channel in message.guild.channels:
                # channel = discord.TextChannel()
                if isinstance(channel, (discord.VoiceChannel, discord.CategoryChannel)):
                    continue
                if channel.nsfw:
                    continue
                # print(channel.name)
                try:
                    async for mess in channel.history(after=datetime.datetime.now() - datetime.timedelta(days=1),
                                                      limit=None):
                        if mess.content.startswith(("!", ":", "?", ".", "~", "`", "このサーバー")) or mess.author.bot:
                            continue
                        text = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", mess.content)
                        text = re.sub(r'```.+```', "", text)
                        text = re.sub(r'<.+>', "", text)
                        text = re.sub(r':.+:', "", text)
                        text = re.sub(r'[!-/:-@[-`{-~]', "", text)
                        trands = []
                        for token in self.t.tokenize(text, stream=True):
                            part_of_speech = token.part_of_speech.split(",")
                            if part_of_speech[0] in ["名詞", "一般名詞", "固有名詞"]:
                                if part_of_speech[1] == "代名詞" and part_of_speech[2] == "一般":
                                    # print(token.surface, " -> ", token.part_of_speech)
                                    continue
                                if len(token.surface) < 2 or len(set(token.surface)) == 1:
                                    continue
                                try:
                                    b = int(token.surface)
                                    continue
                                except:
                                    pass
                                trands.append(token.surface)
                                # print(token.surface)
                        counter += set(trands)
                        time = int(mess.created_at.timestamp())
                        sisu = time - (now - 86400)
                        # print(sisu)
                        for x in set(trands):
                            solt.append((x, sisu))
                except:
                    continue
        elif msg.content == "全体":
            if not message.author.id == 212513828641046529: return
            for channel in self.client.get_all_channels():
                # channel = discord.TextChannel()
                if isinstance(channel, (discord.VoiceChannel, discord.CategoryChannel)):
                    continue
                if channel.nsfw:
                    continue
                # print(channel.name)
                try:
                    async for mess in channel.history(after=datetime.datetime.utcnow() - datetime.timedelta(days=1),
                                                      limit=None):
                        if mess.content.startswith(("!", ":", "?", ".", "~", "`", "このサーバー")) or mess.author.bot:
                            continue
                        text = re.sub(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-…]+', "", mess.content)
                        text = re.sub(r'```.+```', "", text)
                        text = re.sub(r'<.+>', "", text)
                        text = re.sub(r':.+:', "", text)
                        text = re.sub(r'[!-/:-@[-`{-~]', "", text)
                        trands = []
                        for token in self.t.tokenize(text, stream=True):
                            if token.part_of_speech.split(",")[0] in ["名詞", "一般名詞", "固有名詞"]:
                                if token.part_of_speech.split(",")[1] == "代名詞":
                                    print(token.surface," -> ",token.part_of_speech)
                                if len(token.surface) < 2 or len(set(token.surface)) == 1:
                                    continue
                                try:
                                    b = int(token.surface)
                                    continue
                                except:
                                    pass
                                trands.append(token.surface)
                                # print(token.surface)
                        counter += set(trands)
                        time = int(mess.created_at.timestamp())
                        sisu = time - now
                        # print(sisu)
                        for x in set(trands):
                            solt.append((x, sisu))
                except:
                    continue
        res = {}
        for y in solt:
            if y[0] in res.keys():
                res[y[0]] += y[1]
                continue
            res[y[0]] = y[1]
        c = sorted(res.items(), key=lambda x: x[1], reverse=True)
        embed = discord.Embed(title="トレンド", description="ここ1日のトレンドを表示します")
        ty = ""
        try:
            for x in range(20):
                embed.add_field(name=c[x][0], value=c[x][1])
        except IndexError:
            pass
        for x in range(len(c)):
            ty += f'{c[x][0]},{c[x][1]}\n'
        await msg_channel.send(embed=embed)
        ty += f'{message.guild.name}, {message.guild.id}, len {len(c)}'
        await owner.send(ty)

    async def shiritori(self, message: discord.Message):
        if message.author.id in self.is_shiritori:
            return
        self.is_shiritori.append(message.author.id)

        def pred(m):
            return m.author == message.author and m.channel == message.channel
        await message.channel.send("しりとりしよう！最後にアルファベットは来ないようにしてね！\n私から行くよ、最初は、\nしりとり [り]")
        words = ["しりとり"]
        last_word = "り"
        channel = message.channel
        while True:
            try:
                mess = await self.client.wait_for('message', check=pred, timeout=60)
            except asyncio.TimeoutError:
                await message.channel.send("早く答えないなら終わるね！私の勝ち！")
                self.is_shiritori.remove(message.author.id)
                return False
            if re.match("[a-zA-Z0-9]", mess.content[-1]):
                await channel.send("最後を数字かアルファベットにしないで！私の勝ち！")
                self.is_shiritori.remove(message.author.id)
                return
            conv_text = self.conv.do(mess.content)
            if conv_text[-1] == "ん":
                await channel.send("`ん`はダメだよーw！私の勝ち！")
                self.is_shiritori.remove(message.author.id)
                return
            if conv_text in words:
                await channel.send("その単語はもう出たよ！私の勝ち！")
                self.is_shiritori.remove(message.author.id)
                return
            if conv_text[0] != last_word:
                await channel.send("単語の最初が違う！私の勝ち！")
                self.is_shiritori.remove(message.author.id)
                return
            token = list(set([i.part_of_speech[0:2] for i in self.t.tokenize(mess.content)]))
            if not len(token) == 1 or token[0] != "名詞":
                await channel.send("そんな単語ないよ！私の勝ち！")
                self.is_shiritori.remove(message.author.id)
                return
            s_word = search_word(mess.content)
            if not s_word:
                await channel.send("そんな単語ないよ！私の勝ち！")
                self.is_shiritori.remove(message.author.id)
                return
            last_word = conv_text[-1]
            w = search_word_from_jiten(last_word, words, self.t)
            last_word = w[-2]
            words.append(w)
            await channel.send(f"じゃあねえ...{w}で。\nどうぞ->")

    async def command(self, message: discord.Message, command: str, args: list, point: int):
        if command == "!trend":
            await self.trend(message)
            return True
        if command == "!data":
            await self.get_data(message)
            return True

    async def dialogue(self, message: discord.Message):

        if message.author.id in self.is_shiritori:
            return
        if message.content == "-not":
            try:
                if message.channel.id in self.not_rlearn_channel:
                    self.not_rlearn_channel.remove(message.channel.id)
                    await message.channel.send("設定完了-削除")
                else:
                    self.not_rlearn_channel.append(message.channel.id)
                    await message.channel.send("設定完了-追加")
                return
            except:
                return
        content = message.clean_content
        if message.channel.is_nsfw():
            return
        for x in cannnot_words:
            if x in message.content:
                return
        # if len(content) > 3 or message.channel.id in self.not_rlearn_channel and message.author.id == 212513828641046529:
        #     chain = PrepareChain(content)
        #     triplet_freqs = chain.make_triplet_freqs()
        #     chain.save(triplet_freqs)
        generated = self.generator.generate(content, _wadai=self.wadai, low=True)
        content = generated[0]
        self.wadai = generated[1]
        print(self.wadai)
        if content:
            await message.channel.send(content)
            await self.log_channel.send(f"```\n{message.content} from {message.author.name}(id:{message.author.id})\n"
                                        f"guild: {message.guild.name}(id:{message.guild.id})\n```")

    async def dialogue_own(self, message: discord.Message):
        generator1 = GenerateText(n=1, db="./datas/chain1.db")
        generator2 = GenerateText(n=1, db="./datas/chain2.db")
        start = await message.channel.send("ねえねえ")
        mess = start
        for x in range(50):
            content = generator1.generate(mess.content.replace("```\nclone2\n```\n", ""))
            if content:
                mess = await message.channel.send("```\nclone1\n```\n" + content)
            await asyncio.sleep(2)
            content = generator2.generate(mess.content.replace("```\nclone1\n```\n", ""))
            if content:
                mess = await message.channel.send("```\nclone2\n```\n" + content)
            await asyncio.sleep(2)

    async def on_message(self, message: discord.Message):
        if message.channel.id in [501902669695418368, 501927723627970560, 501904504485183489, 501974208319062026, 433572196548345866, 502425962969956352]:
            self.client.loop.create_task(self.dialogue(message))
            return True

        def pred(m):
            return m.author == message.author and m.channel == message.channel
        if message.content.startswith("すみどらちゃん"):
            await message.channel.send("なあに？\n(わからなかったら何ができる？って聞いてね)")
            try:
                mess = await self.client.wait_for('message', check=pred, timeout=30)
            except asyncio.TimeoutError:
                await message.channel.send("用事がないなら帰るね！")
                return False
            content = mess.content
            channel = mess.channel
            guild = message.guild

            async def send_waiting():
                if re.match("(なに|何)が(できる|出来る)(\?|？)", content):
                    await channel.send(what_to_do)
                    return True
                if re.search("おみくじ", content):
                    await omikuzi(message)
                    return True
                if re.search(what_do_say, content):
                    groups = re.search(what_do_say, content).groups()
                    before, after = groups[0], groups[3]
                    if guild.id in self.say_b_a.keys():
                        self.say_b_a[guild.id][before] = after
                    else:
                        self.say_b_a[guild.id] = {before: after}
                    await channel.send(f"{before}って言ってたら{after}って言えばいいんだね！私覚えた！")
                    return True
                if re.search(".*このチャンネルで(挨拶|あいさつ)して.*", content):
                    self.hello_channel_ids[message.guild.id] = message.channel.id
                    await channel.send("わかった！このチャンネルであいさつするね！")
                    return True
                if re.search(".*ニックネーム.*(覚えて|おぼえて).*", content):
                    await channel.send("おっけー！")
                    self.user_nick[message.author.id] = message.author.display_name
                    return True
                if re.search("なんでもない", content):
                    await channel.send("わかったー")
                    return True
                if re.search(".*(覚えている|覚えてる|おぼえている|おぼえてる).*(言葉|ことば).*(見せて|みせて).*", content):
                    await channel.send("わかったー\nえーっと...")
                    async with channel.typing():
                        await asyncio.sleep(2)
                        dic = self.say_b_a[message.guild.id]
                        text = "```cpp\nユーザーが言うことば : 返すことば\n"
                        for key, value in dic.items():
                            text += f"{key} : {value}\n"
                            if len(text) > 1900:
                                break
                        await channel.send(text + "\n```")
                        return True
                if content == "クローンと会話" and message.author.id == 212513828641046529:
                    self.client.loop.create_task(self.dialogue_own(message))
                    return True
                if re.search(".*しりとり.*", content):
                    self.client.loop.create_task(self.shiritori(message))
                    return True
                _content = self.generator.generate(content)
                if _content:
                    await message.channel.send(_content)
                return True
            await send_waiting()
        try:
            if not message.guild:
                return
            if message.content in self.say_b_a[message.guild.id]:
                await message.channel.send(self.say_b_a[message.guild.id][message.content])
        except KeyError:
            self.say_b_a[message.guild.id] = {}
        return True

    async def dicset(self, message: discord.Message):
        content = message.content.split(",")
        del content[0]
        with open(self.dic_url, 'a') as f:
            f.write(f"{content[1]},{content[2]},{content[3]}\n")
        await message.channel.send(f"{content[1]},{content[2]},{content[3]}\nとして書き込みました。")
        self.t = Tokenizer(self.dic_url, udic_type="simpledic", udic_enc="utf8")
        self.generator.reload()

    async def logout(self):
        with open('./datas/say.pickle', mode='wb') as f:
            pickle.dump(self.say_b_a, f)
        with open('./datas/hello.pickle', mode='wb') as f:
            pickle.dump(self.hello_channel_ids, f)
        with open('./datas/nick.pickle', mode='wb') as f:
            pickle.dump(self.user_nick, f)

    async def member_join(self, member: discord.Member):
        await asyncio.sleep(1)
        if member.guild.id in self.hello_channel_ids.keys():
            channel = self.client.get_channel(self.hello_channel_ids[member.guild.id])
            message = random.choice(hello)
            message = message.format(user=member)
            await channel.send(message)
        if member.id in self.user_nick.keys():
            nick = self.user_nick[member.id]
            await member.edit(nick=nick)
            if member.guild.id in self.hello_channel_ids:
                await self.client.get_channel(self.hello_channel_ids[member.guild.id]).send(
                    f"{member.display_name}さんのニックネーム変えてあげた！")

    async def member_remove(self, member: discord.Member):
        await asyncio.sleep(1)
        if member.guild.id in self.hello_channel_ids.keys():
            channel = self.client.get_channel(self.hello_channel_ids[member.guild.id])
            await channel.send(f"{member.name}さんが去って行っちゃった...")
