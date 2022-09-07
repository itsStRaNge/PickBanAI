import time

import requests
import pandas as pd
import sqlite3
from bs4 import BeautifulSoup

URL = "https://gol.gg/game/stats/%s/page-game/"
TEAM_OFFSET = 10


def get_game_page(game_id: int) -> BeautifulSoup:
    page = requests.get(URL % game_id, headers={
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        "upgrade-insecure-requests": "1",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "authority": "gol.gg"
    })
    if page.status_code == 200:
        return BeautifulSoup(page.content, "html.parser")
    raise ValueError


def extract_game(game_page: BeautifulSoup) -> ([str], bool):
    all_champs = []
    win = "WIN" in str(game_page.find("div", {"class": "col-12 blue-line-header"}))
    for d in game_page.find_all("div", {"class": "col-10"}):
        for i in d.find_all('img'):
            champ = i.get("alt")
            all_champs.append(champ)
    return all_champs, win


def format_game(game_id: int, champs: [str], win: bool) -> {}:
    return {
        "game_id": game_id,
        "win": "BLUE" if win else "RED",
        "blue_b1": champs[0],
        "red_b1": champs[TEAM_OFFSET],
        "blue_b2": champs[1],
        "red_b2": champs[1 + TEAM_OFFSET],
        "blue_b3": champs[2],
        "red_b3": champs[2 + TEAM_OFFSET],

        "blue_p1": champs[5],
        "red_p1": champs[5 + TEAM_OFFSET],
        "red_p2": champs[6 + TEAM_OFFSET],
        "blue_p2": champs[6],
        "blue_p3": champs[7],
        "red_p3": champs[7 + TEAM_OFFSET],

        "blue_b4": champs[3 + TEAM_OFFSET],
        "red_b4": champs[3 + TEAM_OFFSET],
        "blue_b5": champs[4 + TEAM_OFFSET],
        "red_b5": champs[4 + TEAM_OFFSET],

        "red_p4": champs[8 + TEAM_OFFSET],
        "blue_p4": champs[8 + TEAM_OFFSET],
        "blue_p5": champs[9 + TEAM_OFFSET],
        "red_p5": champs[9 + TEAM_OFFSET],
    }

def main():
    all_games = []
    error_count = 0
    game_id = 1002
    while True:
        try:
            print(f"Extracting game {game_id}")
            game_page = get_game_page(game_id)
            champs, win = extract_game(game_page)
            all_games.append(format_game(game_id, champs, win))
            error_count = 0
        except ValueError:
            if error_count == 0:
                print("Could not parse game, retrying")
                game_id -= 1  # retry
                time.sleep(2)
            elif error_count > 3:
                break
            else:
                time.sleep(0.5)
            error_count += 1
        finally:
            game_id += 1

    df = pd.DataFrame(all_games)
    print(df)

    cnx = sqlite3.connect('database.sqlite')
    df.to_sql(name='pickban', con=cnx)
    # pd.read_sql('select * from price2', cnx)

main()