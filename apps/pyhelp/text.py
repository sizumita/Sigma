import discord
events = ["on_connect()", "on_ready()", "on_shard_ready(shard_id)", "on_resumed()", "on_error(event, *args, **kwargs)",
          "on_socket_raw_receive(msg)", "on_socket_raw_send(payload)", "on_typing(channel, user, when)",
          "on_message(message)", "on_message_delete(message)", "on_raw_message_delete(payload)",
          "on_raw_bulk_message_delete(payload)", "on_message_edit(before, after)", "on_raw_message_edit(payload)",
          "on_reaction_add(reaction, user)", "on_raw_reaction_add(payload)", "on_reaction_remove(reaction, user)",
          "on_raw_reaction_remove(payload)", "on_reaction_clear(message, reactions)", "on_raw_reaction_clear(payload)",
          "on_private_channel_delete(channel)", "on_private_channel_create(channel)",
          "on_private_channel_update(before, after)", "on_private_channel_pins_update(channel, last_pin)",
          "on_guild_channel_delete(channel)", "on_guild_channel_create(channel)",
          "on_guild_channel_update(before, after)", "on_guild_channel_pins_update(channel, last_pin)",
          "on_webhooks_update(channel)", "on_member_join(member)", "on_member_remove(member)",
          "on_member_update(before, after)", "on_guild_join(guild)", "on_guild_remove(guild)",
          "on_guild_update(before, after)", "on_guild_role_create(role)", "on_guild_role_delete(role)",
          "on_guild_role_update(before, after)", "on_guild_emojis_update(guild, before, after)",
          "on_guild_available(guild)", "on_guild_unavailable(guild)", "on_voice_state_update(member, before, after)",
          "on_member_ban(guild, user)", "on_member_unban(guild, user)", "on_group_join(channel, user)",
          "on_group_remove(channel, user)", "on_relationship_add(relationship)", "on_relationship_remove(relationship)",
          "on_relationship_update(before, after)"
          ]
send_message = """
```py
# メッセージの送信
await channel.send('テキストをここに')
#embedの送信
await channel.send(embed=embed)

await ctx.send("テスト", tts=True)  # ttsメセージを送信。権限がない場合は、ttsを使えずに送信されます （例外は送出されません）
```
"""
send_file = """
```py
await channel.send(file=discord.File("image.png"))  # ディスクからファイルを送信

# 複数のファイルを送信
a = discord.File("a.png")
b = discord.File("b.png")
await channel.send(files=[a, b])

# バイナリストリームをファイルとして送信
from io import BytesIO
import aiohttp

async with aiohttp.ClientSession() as cs:
    async with cs.get("https://www.python.org/static/img/python-logo.png") as resp:
        data = await resp.read()

buffer = BytesIO(data)
await channel.send(file=discord.File(fp=buffer, filename="image.png"))
```
"""
wait_for_message = """
```py
@client.event
async def on_message(message):
    if message.content.startswith('$greet'):
        channel = message.channel
        await channel.send('Say hello!')

        def check(m):
            return m.content == 'hello' and m.channel == channel

        msg = await client.wait_for('message', check=check)
        await channel.send(f'Hello {msg.author}!')
```
"""
wait_for_reaction = """
```py
@client.event
async def on_message(message):
    if message.content.startswith('$thumb'):
        channel = message.channel
        await channel.send('Send me that 👍 reaction, mate')

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) == '👍'

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await channel.send('👎')
        else:
            await channel.send('👍')
```
"""
how_to_event = """
```py
@client.event
async def event_name(args):
    ...
```
"""


def get_help_bot(text, flags):
    pass


def get_help(text, flags):
    if "-bot" in flags:
        return get_help_bot(text, flags)
    if text == "send_message":
        return send_message
    elif text == "send_file":
        return send_file
    elif text == "send":
        embed = discord.Embed(description="send_message\nsend_file")
        return embed
    elif text == "wait_for":
        if "-message" in flags:
            return wait_for_message
        elif "-reaction" in flags:
            return wait_for_reaction
        return discord.Embed(title="wait_for", description="-message\n-reaction")
    elif text == "event":
        if "-all" in flags:
            text = "```py\nevents:\n"
            for x in events:
                text += x + "\n"
            return text + "```"
        return how_to_event
    elif text == "list":
        embed = discord.Embed(title="Discord.py help", description="Discord.pyに付いてのヘルプを表示します。\n"
                                                                   "使用方法: ?py [関数名] [-reaction -message ...]")
        embed.add_field(name="send", value="send_message\nsend_file")
        embed.add_field(name="wait_for", value="-message\nreaction")
        embed.add_field(name="event", value="-all")
        return embed
