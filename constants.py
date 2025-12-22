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

BATTLE_ATTRIBUTES = ["power", "toughness", "planeswalker_loyalty"]

DROP_COLUMNS = ["artist", "cmc", "color_identity",
                "games", "keywords", "lang",
                "layout", "legalities", "loyalty",
                "object", "printed_name", "produced_mana",
                "rarity", "released_at", "set",
                "set_id", "set_name", "set_type",
                "standard", "future", "historic",
                "timeless", "gladiator", "pioneer", 
                "explorer", "modern", "legacy", 
                "pauper", "vintage", "penny", 
                "commander", "oathbreaker", "standardbrawl", 
                "brawl", "alchemy", "paupercommander", 
                "duel", "oldschool", "premodern", 
                "predh", "legal_sum"]

STOPWORDS = ['a', 'about', 'above',
             'after', 'again', 'against',
             'ain', 'all', 'am',
             'an', 'and', 'any',
             'are', 'aren', "aren't",
             'as', 'at', 'be',
             'because', 'been', 'before',
             'being', 'below', 'between',
             'both', 'but', 'by',
             'can', 'couldn', "couldn't",
             'd', 'did', 'didn',
             "didn't", 'do', 'does',
             'doesn', "doesn't", 'doing',
             'don', "don't", 'down',
             'during', 'each', 'few',
             'for', 'from', 'further',
             'had', 'hadn', "hadn't",
             'has', 'hasn', "hasn't",
             'have', 'haven', "haven't",
             'having', 'he', "he'd",
             "he'll", 'her', 'here',
             'hers', 'herself', "he's",
             'him', 'himself', 'his',
             'how', 'i', "i'd",
             'if', "i'll", "i'm",
             'in', 'into', 'is',
             'isn', "isn't", 'it',
             "it'd", "it'll",
             "it's", 'its', 'itself',
             "i've", 'just', 'll',
             'm', 'ma', 'me',
             'mightn', "mightn't", 'more',
             'most', 'mustn', "mustn't",
             'my', 'myself', 'needn',
             "needn't", 'no', 'nor',
             'not', 'now', 'o',
             'of', 'off', 'on',
             'once', 'only', 'or',
             'other', 'our', 'ours',
             'ourselves', 'out', 'over',
             'own', 're', 's',
             'same', 'shan', "shan't",
             'she', "she'd", "she'll",
             "she's", 'should', 'shouldn',
             "shouldn't", "should've", 'so',
             'some', 'such', 't',
             'than', 'that', "that'll",
             'the', 'their', 'theirs',
             'them', 'themselves', 'then',
             'there', 'these', 'they',
             "they'd", "they'll", "they're",
             "they've", 'this', 'those',
             'through', 'to', 'too',
             'under', 'until', 'up',
             've', 'very', 'was',
             'wasn', "wasn't", 'we',
             "we'd", "we'll", "we're",
             'were', 'weren', "weren't",
             "we've", 'what', 'when',
             'where', 'which', 'while',
             'who', 'whom', 'why',
             'will', 'with', 'won',
             "won't", 'wouldn', "wouldn't",
             'y', 'you', "you'd",
             "you'll", 'your', "you're",
             'yours', 'yourself', 'yourselves',
             "you've"]
    
SCRYFALL_CARDS_URL = "https://data.scryfall.io/default-cards/default-cards-20250413212519.json"
SCRYFALL_SUPERTYPES_URL = "https://api.scryfall.com/catalog/supertypes"
SCRYFALL_CARD_TYPES_URL = "https://api.scryfall.com/catalog/card-types"
SCRYFALL_ARTIFACT_TYPES_URL = "https://api.scryfall.com/catalog/artifact-types"
SCRYFALL_CREATURE_TYPES_URL = "https://api.scryfall.com/catalog/creature-types"
SCRYFALL_ENCHANTMENT_TYPES_URL = "https://api.scryfall.com/catalog/enchantment-types"
SCRYFALL_LAND_TYPES_URL = "https://api.scryfall.com/catalog/land-types"
SCRYFALL_PLANESWALKER_TYPES_URL = "https://api.scryfall.com/catalog/planeswalker-types"
SCRYFALL_SPELL_TYPES_URL = "https://api.scryfall.com/catalog/spell-types"
SCRYFALL_KEYWORD_ABILITIES_URL = "https://api.scryfall.com/catalog/keyword-abilities"
SCRYFALL_KEYWORD_ACTIONS_URL = "https://api.scryfall.com/catalog/keyword-actions"
SCRYFALL_ABILITY_WORD_URL = "https://api.scryfall.com/catalog/ability-words"


