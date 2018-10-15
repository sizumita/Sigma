"""
```
Sigma menu v1.0.0
----------
status: 正常
User: {user.name}

commands:

sigma contract -> すみどらちゃん|Sigma 利用規約を表示します。

sigma help -> Sigma help centerを起動します。

~~sigma game -> Sigma game centerを起動します。~~

~~sigma settings -> 設定画面を開きます。~~

~~sigma server manage -> Sigma Server Controlを起動します。（Administer必須）~~

~~sigma gui -> Sigma GUI (v1.0.0)を開きます。~~

sigma apps -> Sigma Apps を起動します。

~~sigma shutdown -> Sigma をシャットダウンします。~~

Sigma:~ {user.name}$
```
"""
from classes.baseworker import BaseWorker
from classes.yahoo_api import Yahoo_API
from classes.decos import owner_only
import discord
import asyncio
import io
import re
import textwrap
from contextlib import redirect_stdout, redirect_stderr
import traceback
import requests
import pandas as pd
from bs4 import BeautifulSoup
from classes.math.Graph import pie_chart
user = {}
REPORT_CHANNEL = 496115423603851265
notice_CHANNEL = 494883023339257868
help_message = """
```
Sigma OS v1.0.0

Sigma main kernel です。

commands:

!os report [レポート文] 違反のレポートや、機能改善などの要望を言えます。

!os news Yahoo Newsを取得します。

!emoji [unicodeコード] unicodeコードに対応した絵文字をリアクションします。

!emoji [絵文字] 絵文字に対応したunicodeコードを表示します。
```
"""
menu = """
```
Sigma menu v1.0.0
----------
status: 正常
User: {user.name}

commands:

sigma contract -> すみどらちゃん|Sigma 利用規約を表示します。

# sigma help -> Sigma help centerを起動します。

sigma apps -> Sigma Apps を起動します。

Sigma:~ {user.name}$
```
"""
contract_e = discord.Embed(title="すみどらちゃん|Sigma 利用規約", description="すみどらちゃん|Sigmaは、Discordのさらなる発展を目指してシステムです。\n"
                                                                   "このシステムでは、サーバーの規定は反映されず、\n下記の利用規約が適応されます。", inline=False)
contract_e.add_field(name="本規約について", value='この利用規約（以下，「本規約」といいます。）は，すみどらちゃんコミュニティチーム（以下，「当チーム」といいます。）\n'
                                           'が提供するサービス"すみどらちゃん|Sigma"(以下，「本サービス」といいます。）の利用条件を定めるものです。\n'
                                           '利用ユーザーの皆さま（以下，「ユーザー」といいます。）には，本規約に従い本サービスをご利用いただきます。', inline=False)
contract_e.add_field(name="第1条（適用）", value="本規約は，ユーザーと当チームとの間の本サービスの利用に関わる一切の関係に適用されるものとします。", inline=False)
contract_e.add_field(name="第2条（禁止事項）", value='''
ユーザーは，本サービスの利用にあたり，以下の行為をしてはなりません。
（1）法令または公序良俗に違反する行為
（2）犯罪行為に関連する行為
（3）当チームのサーバーまたはネットワークの機能を破壊したり，妨害したりする行為
（4）当チームのサービスの運営を妨害するおそれのある行為
（5）他のユーザーに関する個人情報等を収集または蓄積する行為
（6）他のユーザーに成りすます行為
（7）当チームのサービスに関連して，反社会的勢力に対して直接または間接に利益を供与する行為
（8）当チーム，本サービスの他の利用者または第三者の知的財産権，肖像権，プライバシー，名誉その他の権利または利益を侵害する行為
（9）過度に暴力的な表現，露骨な性的表現，人種，国籍，信条，性別，社会的身分，門地等による差別につながる表現，自殺，自傷行為，薬物乱用を誘引または助長する表現，その他反社会的な内容を含み他人に不快感を与える表現を，投稿または送信する行為
（10）他のお客様に対する嫌がらせや誹謗中傷を目的とする行為，その他本サービスが予定している利用目的と異なる目的で本サービスを利用する行為
（11）宗教活動または宗教団体への勧誘行為
（12）その他，当チームが不適切と判断する行為
（13) Discord利用規約に違反する行為
 (14) discordのinviteを投稿する行為
''', inline=False)
contract_e.add_field(name="第3条（利用制限および登録抹消）", value='''
当チームは以下の場合等には，事前の通知なく投稿データを削除し，ユーザーに対して本サービスの全部もしくは一部の利用を制限し、またはユーザーとしての登録を抹消することができるものとします。
（1）本規約のいずれかの条項に違反した場合
（2）当チームからの問い合わせその他の回答を求める連絡に対して7日間以上応答がない場合
（3）その他，当チームが本サービスの利用を適当でないと判断した場合
当チームは，当チームの運営行為によりユーザーに生じたいかなる損害についても、一切の責任を免責されるものとします。
また、ユーザー様同士のトラブルにつきましては、自己責任による当事者同士の解決を基本とし、当チームは一切の責任を免責されるものとします。
''')
point_menu = """

"""


def cleanup_code(content):
    """Automatically removes code blocks from the code."""
    # remove ```py\n```
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`

    return content.strip('` \n')


class Worker(BaseWorker):
    def __init__(self, client: discord.Client):

        super().__init__(client)
        self._last_result = None
        self.r = requests.get("https://ja.wikipedia.org/wiki/Unicode%E3%81%AEEmoji%E3%81%AE%E4%B8%80%E8%A6%A7")
        self.soup = BeautifulSoup(self.r.text, 'lxml')
        self.report = client.get_channel(REPORT_CHANNEL)
        self.notice = client.get_channel(notice_CHANNEL)

    async def join(self, message: discord.Message):
        # ここにかく
        await message.channel.send(help_message)
        return True

    async def command(self, message: discord.Message, command: str, args: list, point: int):
        def pred(m):
            return m.author == message.author and m.channel == message.channel

        @owner_only
        async def my_eval(author: discord.Member, message: discord.Message):
            env = {
                'client': self.client,
                'message': message,
                'channel': message.channel,
                'author': message.author,
                'guild': message.guild,
                '_': self._last_result,
                'soup': self.soup
            }

            env.update(globals())
            await message.channel.send("コードを入力してください")
            try:
                mess = await self.client.wait_for('message', check=pred, timeout=30)
            except asyncio.TimeoutError:
                return False
            body = cleanup_code(mess.content)
            stdout = io.StringIO()
            to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'
            try:
                exec(to_compile, env)
            except Exception as e:
                return await message.channel.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            func = env['func']

            try:
                with redirect_stdout(stdout):
                    ret = await func()
                with redirect_stderr(stdout):
                    pass
            except Exception as e:
                value = stdout.getvalue()
                await message.channel.send(f'```py\n{value}{traceback.format_exc()}\n```')
            else:
                value = stdout.getvalue()
                try:
                    await mess.add_reaction('\u2705')
                except:
                    pass

                if ret is None:
                    if value:
                        await channel.send(f'```py\n{value}\n```')
                else:
                    self._last_result = ret
                    await channel.send(f'```py\n{value}{ret}\n```')

        @owner_only
        async def command_graph(author: discord.Member, message: discord.Message):
            df = pd.read_csv('./logs/command.csv', header=None, sep="®")
            df_list = df.values.tolist()
            df_col_datas = {}
            # ['sigma', 'sigma globalchat', 3.5239478444032e+17, 4.448176198628147e+17, '477080222286479397',
            #  '2018-10-06 13:19:03']
            for data in df_list:
                # print(data[0])
                if data[0] in df_col_datas.keys():
                    df_col_datas[data[0]] += 1
                    continue
                df_col_datas[data[0]] = 1
            col = []
            data = []
            await message.channel.send(df_col_datas)
            for key, value in df_col_datas.items():
                col.append(key)
                data.append(value)
            pie_chart(data, col, "./apps/os/data/command.png")
            file = discord.File("./apps/os/data/command.png")
            await message.channel.send("app 使用率のグラフです。", file=file)

        @owner_only
        async def notice(author: discord.Member):
            text = " ".join(args)
            await self.notice.send(text)
        channel = message.channel
        author = message.author
        if command == ".notice":
            await notice(message.author)
            return True
        if command == "sigma":
            if not args:
                await channel.send(menu.format(user=message.author))
                return True
            if args[0] == "menu":
                await channel.send(menu.format(user=message.author))
                return True
            if args[0] == "apps":
                return "apps"
            if args[0] == "stop":
                if not author.id == 212513828641046529:
                    return False
                self.client.loop.stop()
                return True
            if args[0] == "contract":
                await author.send(embed=contract_e)
                return True
            if args[0] == "point":
                embed = discord.Embed(title=f"{message.author.name}さんのpoint", description=f"{point}ポイント")
                embed.add_field(name="ポイント入金（未実装）", value="実装まで今しばらくお待ちください。")
                await message.channel.send(embed=embed)
                return True
            if args[0] == "link":
                await message.author.send("https://discordapp.com/api/oauth2/authorize?"
                                          "client_id=437917527289364500&permissions=8&scope=bot")
                return True
        if command == "!os":
            if args[0] == "com_logs":
                await command_graph(message.author, message)
            if args[0] == "eval":
                await my_eval(message.author, message)
                return True
            if args[0] == "news":
                api = Yahoo_API()
                embed = api.get_news()
                await message.channel.send(embed=embed)
                return True
            if args[0] == "report":
                del args[0]
                report = " ".join(args)
                await self.report.send(f"{message.author.name}さんからレポート:\n```\n{report}\n```\`id:{message.author.id}")
                await channel.send("reportありがとうございます。真摯に対応させていただきます。")
                return True
            if args[0] == "ban":
                if author.id != 212513828641046529:
                    return -5
                uid = re.sub("[<>?@!]", "", args[1])
                await channel.send("追加しました。")
                return "ban " + uid
            if args[0] == "unban":
                if author.id != 212513828641046529:
                    return -5
                uid = re.sub("[<>?@!]", "", args[1])
                await channel.send("削除しました。")
                return "unban " + uid
        if command == "!emoji":
            try:
                if args[0].startswith('\\u'):
                    try:
                        emoji = self.soup.find_all("td", text=args[0].replace("\\u", "U+").upper())[0]
                        code = emoji.find_parent().find_all('td')[0].find('span').find('a').text
                        await self.client.http.add_reaction(message_id=message.id, channel_id=channel.id, emoji=code)
                        return True
                    except:
                        await channel.send("そんなのないよ")
                        return False
                moto = args[0]
                code = ascii(moto).replace("'", "").replace("000", "").lower()
                await channel.send(f'{moto}のコードは`{code}`です。')
            except IndexError:
                raise

