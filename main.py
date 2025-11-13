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
import logging
import utils # utility functions from other script
# constants for main functon
from constants import SELECTED_COLUMNS, BASIC_LAND_TYPES, CARD_LAYOUTS, CARD_TYPES, COLORS_DICT, COLORS, GAME_FORMATS, SCRYFALL_CARDS_URL, RARITY

processor = MTGDataProcessor(
    
    selected_columns = SELECTED_COLUMNS,
    colors_dict = COLORS_DICT,
    card_types = CARD_TYPES,
    card_subtypes = CARD_SUBTYPES,
    game_formats = GAME_FORMATS,
    non_legal_sets = NON_LEGAL_MAGIC_SETS,
    basic_lands = BASIC_LAND_TYPES,
    card_layout_keep = CARD_LAYOUT_KEEP,
    color_pips_dict = COLOR_PIPS_DICT,
    rarity = RARITY,
    drop_columns = DROP_COLUMNS
)

processor.load_data(SCRYFALL_CARDS_URL)
processor.process_data()
processor.save_data("clean scryfall cards")




