import requests
from bs4 import BeautifulSoup
import re

def parse_ticket_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url} — status {response.status_code}")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {}

    # Extract game name
    h1 = soup.find('h1')
    if h1:
        data['name'] = h1.get_text(strip=True)

    # Extract price
    price_el = soup.find(string=lambda s: s and 'Price' in s)
    if price_el and price_el.parent:
        data['price'] = price_el.parent.get_text(strip=True)

    # Extract odds
    odds_el = soup.find(string=lambda s: s and 'Odds' in s)
    if odds_el and odds_el.parent:
        data['odds'] = odds_el.parent.get_text(strip=True)

    # NEW: Extract total number of tickets printed
    body_text = soup.get_text()
    match = re.search(r"sale of approximately ([\d,]+) tickets", body_text)
    if match:
        total_tickets_str = match.group(1).replace(',', '')
        data['totalTicketsPrinted'] = int(total_tickets_str)

    return data


# Quiet version, for testing or debugging
def parse_ticket_page_quiet(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url} — status {response.status_code}")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {}

    # This will print the whole HTML to help inspect new patterns
    print(soup)

    return data

def get_total_tickets_from_game_id(game_id):
    url = f"https://www.masslottery.com/api/v1/instant-game-prizes?gameID={game_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch {url} — status {response.status_code}")
        return None

    data = response.json()
    try:
        text_nodes = data['prizeTierInfo']['text']['content']
        for paragraph in text_nodes:
            for node in paragraph.get('content', []):
                value = node.get('value', '')
                match = re.search(r"approximately ([\d,]+) tickets", value)
                if match:
                    return int(match.group(1).replace(',', ''))
    except Exception as e:
        pass
        #print(f"Error parsing ticket count for gameID {game_id}: {e}")
    return None
