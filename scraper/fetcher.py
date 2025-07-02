import requests

BASE_URL = 'https://www.masslottery.com'

def get_games():
    url = f'{BASE_URL}/api/v1/games'
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data
    
def build_ticket_url(game):
    return f"{BASE_URL}/games/draw-and-instants/{game['gameIdentifier']}"
