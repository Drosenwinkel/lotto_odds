import requests
from parser import parse_ticket_page,get_total_tickets_from_game_id
from collections import defaultdict
from fetcher import build_ticket_url
import json
from datetime import datetime

BASE_URL = "https://www.masslottery.com"

def compute_roi(prize_tiers, ticket_cost, total_remaining_tickets):
    total_expected_payout = sum(tier['prizeAmount'] * tier['prizesRemaining'] for tier in prize_tiers)
    total_investment = total_remaining_tickets * ticket_cost
    return total_expected_payout / total_investment if total_investment else 0

def format_ticket(ticket_dict):
    if "totalTicketsPrinted" not in ticket_dict:
        raise KeyError(f"Missing 'totalTicketsPrinted' in ticket: {ticket_dict.get('gameName', 'Unknown Game')} - {ticket_dict.get('startDate', 'Unknown Date')}")

    game_name = ticket_dict["gameName"]
    start_date = ticket_dict["startDate"]
    totalTickets = ticket_dict["totalTicketsPrinted"]
    cost = ticket_dict["ticketCost"]

    unclaimed_winning_tickets = 0
    remaining_prize_money = 0
    total_winners = 0
    
    
    #get the number of claimed tickets and the number of winning tickets
    for prize_tier in ticket_dict["prizeTiers"]:
        unclaimed_winning_tickets += prize_tier["prizesRemaining"]
        remaining_prize_money += (prize_tier["prizeAmount"] * prize_tier["prizesRemaining"])
        total_winners += prize_tier["totalPrizes"]

    estimated_percent_unclaimed = unclaimed_winning_tickets / total_winners
    estimated_tickets_remaining = estimated_percent_unclaimed * totalTickets
    return_on_investment = remaining_prize_money / (estimated_tickets_remaining * cost)

    return {"game_name" : game_name, "start_date" : start_date, "return_on_investment" : f"{return_on_investment * 100:.1f}%" , "percent_remaining": f"{estimated_percent_unclaimed * 100:.4f}%"  }



def main():
    try:
        # Get all prize data once
        response = requests.get(f"{BASE_URL}/api/v1/instant-game-prizes")
        response.raise_for_status()
        prize_data_list = response.json()

        # Group by ticket cost
        games_by_cost = {}
        for game_data in prize_data_list:
            ticket_cost = game_data['ticketCost']


            total_tickets = get_total_tickets_from_game_id(game_data['massGameID'])
            if total_tickets:
                game_data['totalTicketsPrinted'] = total_tickets

            games_by_cost.setdefault(ticket_cost, []).append(game_data)
        
        
        
        with open("games_by_cost.json", "w") as f:
            json.dump(games_by_cost, f, indent=2)

        calculated_game_data = defaultdict(list)
        for cost in games_by_cost.keys():
            for game in games_by_cost[cost]:
                try:
                    calculated_game_data[cost].append(format_ticket(game))
                except KeyError as e:
                    print(f"Skipping game due to missing key: {e}")

        
        for cost in calculated_game_data:
            calculated_game_data[cost].sort(key=lambda game: datetime.strptime(game["start_date"], "%Y-%m-%d"), reverse=True)

        

        for key in sorted(calculated_game_data.keys(), reverse = True):
            print(key)
            for game in calculated_game_data[key]:
                print(game)
            
            print()
        
        html = """<html>
                <head><title>Game Data</title></head>
                <body>
                <h1>MASSACHUSETTS STATE LOTTERY ESTIMATED RETURN ON INVESTMENT BY TICKET</h1>
                """
        
        for cost in sorted(calculated_game_data.keys(), reverse=True):
            html += f"<h2>${cost} Tickets</h2>\n"
            html += """
                    <table border="1" cellspacing="0" cellpadding="4">
                    <tr><th>Game Name</th><th>Start Date</th><th>ROI</th><th>% Remaining</th></tr>
                    """
    
            for game in calculated_game_data[cost]:
                html += f"<tr><td>{game['game_name']}</td><td>{game['start_date']}</td><td>{game['return_on_investment']}</td><td>{game['percent_remaining']}</td></tr>\n"
        
            html += "</table><br><br>\n"
        html += "</body></html>"

        with open("/Users/danielrosenwinkel/workspace/rosenwinkel.dev/lotto_odds/index.html", "w") as f:
            f.write(html)

        print("Saved to lottery_games.html")

    except requests.HTTPError as e:
        print(f"HTTP Error: {e}")

if __name__ == "__main__":
    main()
