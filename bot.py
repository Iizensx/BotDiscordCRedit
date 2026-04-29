import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
import random
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
INBOX_CHANNEL_ID = int(os.getenv("INBOX_CHANNEL_ID"))
CREDIT_CHANNEL_ID = int(os.getenv("CREDIT_CHANNEL_ID"))
TICKET_CHANNEL_ID = int(os.getenv("TICKET_CHANNEL_ID"))
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== ระบบสลิป =====

@bot.event
async def on_ready():
    print(f"✅ บอทออนไลน์: {bot.user}")

@bot.event
async def on_message(message):
    if message.channel.id == INBOX_CHANNEL_ID:
        if not message.author.bot:
            if not message.attachments:
                await message.reply("❌ กรุณาแนบรูปสลิปด้วยนะครับ!")
            else:
                lines = message.content.strip().split("\n")
                details = {}
                for line in lines:
                    if ":" in line:
                        key, val = line.split(":", 1)
                        details[key.strip()] = val.strip()

                customer = details.get("ลูกค้า", "ไม่ระบุ")
                amount = details.get("ราคา", "ไม่ระบุ")
                note = details.get("หมายเหตุ", "-")
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                credit_channel = bot.get_channel(CREDIT_CHANNEL_ID)

                for attachment in message.attachments:
                    order_id = f"#{random.randint(10000, 99999)}"

                    embed = discord.Embed(
                        title="✅  จัดส่งสินค้าเรียบร้อยแล้ว",
                        description="━━━━━━━━━━━━━━━━━━━━━━",
                        color=0x57F287
                    )
                    embed.add_field(name="👤  ลูกค้า", value=f"```{customer}```", inline=True)
                    embed.add_field(name="💰  ราคา", value=f"```{amount}```", inline=True)
                    embed.add_field(name="🎫  เลขออเดอร์", value=f"```{order_id}```", inline=True)
                    embed.add_field(name="📝  หมายเหตุ", value=f"```{note}```", inline=False)
                    embed.add_field(name="🕐  วันเวลา", value=f"```{now}```", inline=False)
                    embed.add_field(name="\u200b", value="━━━━━━━━━━━━━━━━━━━━━━", inline=False)
                    embed.set_image(url=attachment.url)
                    embed.set_author(name="IZen Store", icon_url="https://cdn.discordapp.com/embed/avatars/0.png")
                    embed.set_footer(text="✨ IZen store ✨ • ขอบคุณที่ใช้บริการครับ 🙏")
                    embed.timestamp = datetime.utcnow()

                    await credit_channel.send(embed=embed)

                try:
                    await message.add_reaction("✅")
                except:
                    pass

    await bot.process_commands(message)

# ===== ระบบ Ticket =====

class CloseButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 ปิด Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 กำลังปิด Ticket...")
        await interaction.channel.delete()

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 เปิด Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user

        existing = discord.utils.get(guild.text_channels, name=f"ticket-{member.name.lower()}")
        if existing:
            await interaction.response.send_message(f"❌ คุณมี Ticket อยู่แล้วที่ {existing.mention}", ephemeral=True)
            return

        admin_role = guild.get_role(ADMIN_ROLE_ID)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{member.name.lower()}",
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Ticket เปิดแล้ว",
            description=f"สวัสดีครับ {member.mention}\nแอดมินจะมาช่วยเหลือเร็วๆ นี้ครับ\n\nกด **ปิด Ticket** เมื่อเสร็จสิ้น",
            color=0x5865f2
        )
        await channel.send(embed=embed, view=CloseButton())
        await interaction.response.send_message(f"✅ เปิด Ticket แล้วที่ {channel.mention}", ephemeral=True)

@bot.command()
async def setup_ticket(ctx):
    embed = discord.Embed(
        title="🎫 ระบบ Ticket",
        description="กดปุ่มด้านล่างเพื่อเปิด Ticket และพูดคุยกับแอดมินครับ",
        color=0x5865f2
    )
    await ctx.send(embed=embed, view=TicketButton())

bot.run(TOKEN)