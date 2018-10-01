import discord
help_embed = discord.Embed(title="Discord BANs v1.2.0", description="Discord BANsは、Discordを守るために作られました。")
help_embed.add_field(name=".gban [ユーザーid もしくは mention] [理由]", value="Gbanします。Gbanした記録は残され、"
                                                                    "他のサーバーに通知が行きます。", inline=False)
help_embed.add_field(name=".protect start", value="DiscordBANs Server Protectを発動します。\n"
                                                  "発動された場合、.protect setで設定した役職か、\n"
                                                  "Administerが設定されたユーザー以外が全体メンションまたは招待URlを送信した場合"
                                                  "、削除しキックします。")
help_embed.add_field(name=".protect set [役職idもしくはmention]", value="設定した役職のメンション＆招待送信を許可します。\n"
                                                                  "(サーバー設定とは関係ありません。)")
help_embed.add_field(name="公式サーバー", value="https://discord.gg/fVsAjm9")
help_embed.add_field(name="要望は", value="!os report [要望文]")
help_embed.set_author(name="すみどら#8923",
                      icon_url="https://cdn.discordapp.com/attachments/"
                               "496102995403079682/496103058728550411/SIgma_image.jpg")
