# Stats of Age of Empires II games played in Aoe Bombay discord server using tg-bot

Setup:
`python3.11 -m venv venv`
`source venv/bin/activate`
`pip3 install -r requirements.txt`

Steps:

1. Run `python discord_scraper.py`
<!-- 2. `mv data/match_starts_new.csv data/match_starts.csv`
3. `mv data/match_results_raw_new.csv data/match_results_raw.csv` -->
4. Run `python extract_raw_results.py`
5. Run `python process_data.py`
6. Run `cd streamlit run streamlit/player_dashboard.py`