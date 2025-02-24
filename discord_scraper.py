"""Module for scraping Discord messages."""

import os
import discord
import pandas as pd
from dotenv import load_dotenv


class DiscordScraper(discord.Client):
    """Class for scraping Discord messages."""
    async def on_ready(self):
        """Scrape Discord messages."""
        # channel = client.get_channel(933299509805600778) #tg-bot Aoe2 Bombay
        channel = client.get_channel(1200081751272325170)  # tg-bot Aoe2-Dota2
        # channel = client.get_channel(327134162769281026) #game-discussions
        match_starts = []
        match_results = []
        start_date = end_date = 0
        async for msg in channel.history(limit=2500):
            try:
                if str(msg.author) == "Pubobot#8845" and len(msg.embeds) > 0:  # TG-Bot
                    # if msg.embeds[0].title == '__**Domestic** has started!__':
                    if msg.embeds[0].title and "has started!__" in msg.embeds[0].title:
                        queue = (msg.embeds[0].title).split("**")[1]
                        match_id = int(msg.embeds[0].footer.text.split(":")[-1].strip())
                        team_a_players = (
                            msg.embeds[0].fields[0].value.split("\u200b")[1:]
                        )
                        team_b_players = (
                            msg.embeds[0].fields[1].value.split("\u200b")[1:][:-1]
                        )
                        team_a_players = [
                            int(i.strip("`〈ABCDEFGHIJKLMNOPQRSTUVWXYZ★〉<@> `\n"))
                            for i in team_a_players
                        ]
                        team_b_players = [
                            int(i.strip("`〈ABCDEFGHIJKLMNOPQRSTUVWXYZ★〉<@> `\n"))
                            for i in team_b_players
                        ]

                        map_ = msg.embeds[0].fields[3].value.strip(" `*\xa0")
                        date_created = msg.created_at.date()
                        if not start_date:
                            start_date = date_created
                        end_date = date_created
                        print(date_created)

                        match_start_data = {
                            "match_id": match_id,
                            "date": date_created.strftime("%Y-%m-%d"),
                            "map": map_,
                            "team_a_players": team_a_players,
                            "team_b_players": team_b_players,
                            "queue": queue,
                        }

                        match_starts.append(match_start_data)

                # if str(msg.content).startswith('```markdown\nDomestic'):
                if str(msg.content).startswith("```markdown\n"):
                    # print(msg.content)
                    queue = (msg.content).split("\n")[1].split("(")[0]
                    match_results.append(str(msg.content))
                    # print(str(msg.content))
                    # Domestic(742942) results
                    # -------------
                    # 0. A 952 ⟼ 974
                    # > Sephiroth 1466 ⟼ 1488
                    # > Afterlife 1023 ⟼ 1045
                    # > Ju$TK!Dd!nG 799 ⟼ 821
                    # > FraGStaR 520 ⟼ 542
                    # 1. B 958 ⟼ 936
                    # > SuLTaN 1391 ⟼ 1369
                    # > MODI 1146 ⟼ 1124
                    # > Tragedy 669 ⟼ 647
                    # > adirath 628 ⟼ 606```
            except Exception as e:
                print("Error:", e)
                print(msg.embeds[0].title)
                print(msg.content)
                print(msg.embeds[0].footer.text)
                for i in msg.embeds[0].fields:
                    print(i.name, i.value)

        match_starts_df = pd.DataFrame(match_starts)
        match_starts_df.to_csv(
            f"tw_data/match_starts_{end_date}_{start_date}.csv", index=False
        )

        match_results_df = pd.DataFrame(match_results)
        match_results_df.to_csv(
            f"tw_data/match_results_raw_{end_date}_{start_date}.csv", index=False
        )
        print("done")


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True

    client = DiscordScraper(intents=intents)
    load_dotenv()
    client_secret = os.getenv("DISCORD_CLIENT_TOKEN")
    client.run(client_secret)
