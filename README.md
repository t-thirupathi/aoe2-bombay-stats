# Stats of Age of Empires II games played in Aoe Bombay discord server using tg-bot

Setup:
`python3.11 -m venv venv`
`source venv/bin/activate`
`pip3 install -r requirements.txt`

Steps:

1. Run `python discord_scraper.py`
2. Run `python extract_raw_results.py`
3. Run `python process_data.py`
4. Run `streamlit run streamlit_scripts/player_dashboard.py`
