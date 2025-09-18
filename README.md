Ever wondered what that item you just got does? Whether deaths in this game are permanent? How to fast travel? Game Assist can answer all your questions. Simply type in the game's name to generate a vector database of the game's Fandom wiki, which Game Assist will use to read relevant pages and answer your questions without needing to open 20 tabs, or risking going down a rabbit hole!

To run locally:  
  
Backend:  
Create an OpenAI API key (costs $5 minimum)  
Add this API key to game-assist/game-assist-backend/.env (OPENAI_API_KEY=...)  
`cd game-assist-backend`  
`venv/Scripts/activate`  
`pip install -r requirements.txt`  
`flask run --reload`  
To avoid overloading Fandom's servers or getting your IP blocked, keep the DOCS_PER_SECOND env variable to 1 (this will mean that large wikis take more time to load). To make the loading process faster but less comprehensive, change MAX_DOCS (limits the max number of Fandom pages retrieved for a given wiki).


Frontend:  
`cd game-assist-frontend`  
`npm i`  
`npm start`  


Tech stack:
ChromaDB for local vector DB
Flask + Angular
BeautifulSoup for web scraping
