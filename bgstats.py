import pandas as pd
import json

with open("BGStatsExport-241227060814.json", "r") as file:
    bg_stats = file.read()

data = json.loads(bg_stats)
# df = pd.DataFrame(data)
# print(data['plays'])
plays_df = pd.DataFrame(data["plays"])
print(plays_df.columns)
