# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 22:27:39 2025

@author: holli
"""
import requests
import pandas as pd
import numpy as np
import json
import re
import utils # utility functions from other script
# constants for main functon
from constants import SELECTED_COLUMNS, BASIC_LAND_TYPES, CARD_LAYOUTS, CARD_TYPES, COLORS_DICT, COLORS, GAME_FORMATS, SCRYFALL_CARDS_URL

scryfall_raw_data = get_requested_data(SCRYFALL_CARDS_URL)

write_data_local(df = scryfall_raw_data, raw_data = True, file_name = "raw_scryfall_api_call")

scryfall_clean_data = (scryfall_raw_data
                       .pipe(filter_tokens_and_basic_lands)
                       .pipe(get_card_subtypes)
                       .pipe(is_color)
                       .pipe(is_in_format)
                       .pipe(create_keyword_string)
                       .pipe(create_legalities)
                       .pipe(count_number_of_color_pips)
                       .pipe(double_cards))

write_data_local(df = scryfall_clean_data, raw_data = False, file_name = "clean_scryfall_api_call")


scryfall_clean_data["type_line"] = scryfall_clean_data["type_line"].str.replace(" — ", " - ", regex = True)

card_name_chars = scryfall_clean_data["name"].apply(lambda x: list(x))

card_name_chars = set([current_char for char_list in card_name_chars for current_char in char_list])


# Find rows containing 'É'
matches = scryfall_clean_data[scryfall_clean_data["name"].str.contains("É", regex=False, na=False)]


