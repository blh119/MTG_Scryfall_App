# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 23:29:55 2025

@author: holli
"""

SELECTED_COLUMNS = ["object", "id", "name", "lang",
                    "released_at", "uri", "scryfall_uri", "layout",
                    "mana_cost", "cmc", "type_line", "oracle_text",
                    "color_identity", "keywords", "produced_mana", "legalities",
                    "games", "game_changer", "set_id", "set",
                    "set_name", "set_type", "rarity", "digital",
                    "artist", "textless", "power", "toughness",
                    "loyalty", "printed_name"] 

BASIC_LAND_TYPES = ["Forest", "Mountain", "Island", "Swamp", "Plains"]

CARD_LAYOUTS = ["normal", "adventure", "transform", "split",
                "modal_dfc", "planar", "reversilbe_card", "meld",                                                                                               
                "saga", "class", "case", "flip",
                "leveler", "prototype"]

CARD_TYPES = ["Land", "Legend", "Artifact", "Enchantment", "Aura", "Battle",
              "Instant", "Sorcery", "Creature", "Planeswalker"]

COLORS_DICT = {"blue": "U",
               "red": "R",
               "white": "W",
               "black": "B",
               "green": "G",
               "colorless": ""}

COLORS = ["blue", "red", "white", "black", "green"]


GAME_FORMATS = ["standard", "future", "historic",
                "timeless", "gladiator", "pioneer",
                "explorer", "modern", "legacy",
                "pauper", "vintage", "penny",
                "commander", "oathbreaker", "standardbrawl",
                "brawl", "alchemy", "paupercommander",
                "duel", "oldschool", "premodern", "predh"]

SCRYFALL_CARDS_URL = "https://data.scryfall.io/default-cards/default-cards-20250413212519.json"

DB_HOST = "localhost"
DB_PORT = "5433"
DB_USER = "postgres"
DB_PASSWORDS = pd.read_csv("C:\\Users\\holli\\OneDrive\\Documents\\MTG Scryfall App\Data\\DataBase Password.csv")

