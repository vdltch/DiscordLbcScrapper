import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)
driver.get("https://www.leboncoin.fr")
print(driver.title)
driver.quit()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


seen_ads = {}


categories_map = {
    "voitures": "voitures",
    "jeux_video": "jeux_video",
    "informatique": "informatique",
    "multimedia": "multimedia",
    "mode": "mode",
    "immobilier": "immobilier",
    "services": "services"
   
}

@bot.event
async def on_ready():
    print(f'🤖 Connecté en tant que {bot.user}')

@bot.command()
async def startdeal(ctx, search_term: str, category: str):
    search_term_key = f"{search_term.lower().strip()}_{category.lower().strip()}"
    
    if search_term_key in seen_ads:
        await ctx.send(f"🔁 La surveillance de '**{search_term}**' dans la catégorie '**{category}**' est déjà en cours.")
        return

    if category not in categories_map:
        await ctx.send(f"❌ Catégorie inconnue : **{category}**. Choisis parmi : {', '.join(categories_map.keys())}")
        return

    seen_ads[search_term_key] = set()
    await ctx.send(f"📡 Surveillance de '**{search_term}**' dans '**{category}**' toutes les 60 secondes.")

    async def fetch_and_send_new_deals():
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        cat_path = categories_map[category]
        url = f"https://www.leboncoin.fr/recherche?category={cat_path}&text={search_term.replace(' ', '%20')}&sort=price&order=asc"

        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            annonces = soup.find_all("a", {"data-qa-id": "aditem_container"})

            new_results = []
            for annonce in annonces:
                title_el = annonce.find("p", {"data-qa-id": "aditem_title"})
                price_el = annonce.find("span", {"data-qa-id": "aditem_price"})
                if not title_el or not price_el:
                    continue

                title = title_el.text.strip()
                price = price_el.text.strip()
                link = "https://www.leboncoin.fr" + annonce["href"]

                if link not in seen_ads[search_term_key]:
                    seen_ads[search_term_key].add(link)
                    new_results.append((title, price, link))

            for title, price, link in new_results:
                await ctx.send(f"🆕 **{title}**\n💰 {price}\n🔗 {link}")

        except Exception as e:
            print(f"Erreur : {e}")
            await ctx.send(f"⚠️ Erreur lors de la récupération des annonces pour : {search_term} ({category})")

    @tasks.loop(seconds=60)
    async def monitor_loop():
        await fetch_and_send_new_deals()

    monitor_loop.start()


bot.run('MTM2NjUzNTgxODU0OTc4ODcwMg.GrHlXe.h78bHy0ZL5NrhItIn3i4n57AJBJGjG3fXM2Z8o')
