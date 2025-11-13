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

CARD_TYPES = ["Land", "Legendary", "Artifact", "Enchantment", "Battle",
              "Instant", "Sorcery", "Creature", "Planeswalker", "Vanguard",
              "Kindred"]

CARD_SUBTYPES = ["Equipment", "Vehicle", "Powerstone", "Fortification", "Clue", 
                 "Bobblehead", "Food", "Key", "Treasure", "Aura",
                 "Saga", "Curse", "Room", "Background", "Class",
                 "Case", "Rune", "Shrine", "Siege", "Arcane",
                 "Trap", "Adventure", "Lesson", "Omen"]

RARITY = ["common", "uncommon", "rare", "mythic", "special"]

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

CARD_LAYOUT_KEEP = ["normal", "adventure", "transform", "split",
                    "modal_dfc", "planar", "reversilbe_card", "meld",
                    "saga", "class", "case", "flip",
                    "leveler", "prototype"]

NON_LEGAL_MAGIC_SETS = ["Unglued", "Unhinged", "Unstable", "Unsanctioned",
                        "Unfinity"]

COLOR_PIPS_DICT = {"blue": "U",
                   "red": "R",
                   "white": "W",
                   "black": "B",
                   "green": "G",
                   "colorless": "C"}

DROP_COLUMNS = ["artist", "cmc", "color_identity",
                "games", "keywords", "lang",
                "layout", "legalities", "loyalty",
                "object", "printed_name", "produced_mana",
                "rarity", "released_at", "set",
                "set_id", "set_name", "set_type",
                "mana_cost", "type_line", "standard", 
                "future", "historic", "timeless", 
                "gladiator", "pioneer", "explorer",
                "modern", "legacy", "pauper", 
                "vintage", "penny", "commander", 
                "oathbreaker", "standardbrawl", "brawl", 
                "alchemy", "paupercommander", "duel", 
                "oldschool", "premodern", "predh",
                "legal_sum", "card_type"]

SCRYFALL_CARDS_URL = "https://data.scryfall.io/default-cards/default-cards-20250413212519.json"

DB_HOST = "localhost"
DB_PORT = "5433"
DB_USER = "postgres"
DB_PASSWORDS = pd.read_csv("C:\\Users\\holli\\OneDrive\\Documents\\MTG Scryfall App\Data\\DataBase Password.csv")

