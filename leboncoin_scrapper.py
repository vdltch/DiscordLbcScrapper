import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'🤖 Connecté en tant que {bot.user}')

@bot.command()
async def deal(ctx, *, search_term):
    await ctx.send(f"🔍 Recherche sur LeBonCoin pour : **{search_term}**...")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    url = f"https://www.leboncoin.fr/recherche?text={search_term.replace(' ', '%20')}&sort=price&order=asc"

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        annonces = soup.find_all("a", {"data-qa-id": "aditem_container"})

        results = []

        for annonce in annonces[:10]:
            title_el = annonce.find("p", {"data-qa-id": "aditem_title"})
            price_el = annonce.find("span", {"data-qa-id": "aditem_price"})
            if not title_el or not price_el:
                continue

            title = title_el.text.strip()
            price = price_el.text.strip()
            link = "https://www.leboncoin.fr" + annonce["href"]
            results.append((title, price, link))

        if results:
            best = results[0]
            await ctx.send(f"💸 **{best[0]}**\n💰 {best[1]}\n🔗 {best[2]}")
        else:
            await ctx.send("❌ Aucun résultat trouvé.")

    except Exception as e:
        print(f"Erreur : {e}")
        await ctx.send("⚠️ Une erreur est survenue pendant la recherche.")

bot.run("MTM2NjUzNTgxODU0OTc4ODcwMg.GaoLPE.AIwRJA3OJXt-zIkZB57BjGyKvO3Co22ceYwT8k")
