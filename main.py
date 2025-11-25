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
import nltk
import utils # utility functions from other script
from gensim.models import Word2Vec
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.preprocessing import StandardScaler
nltk.download("punkt_tab")
nltk.download("punkt")

# constants for main functon
from constants import SELECTED_COLUMNS, BASIC_LAND_TYPES, CARD_LAYOUTS, CARD_TYPES, COLORS_DICT, COLORS, GAME_FORMATS, SCRYFALL_CARDS_URL, RARITY, BATTLE_ATTRIBUTES

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
    drop_columns = DROP_COLUMNS,
    battle_attributes = BATTLE_ATTRIBUTES
)

processor.load_data(SCRYFALL_CARDS_URL)
processor.process_data()


card_training_model = CardRecommendorModel(processor)
card_training_model.legal_cards_for_format()
card_training_model.tokenize_text()
card_training_model.trainWord2Vec_model()
card_training_model.average_word_vector_to_df()

pd.to_csv()

processor.df.to_csv("C:\\Users\\holli\\MTG Scryfall App\\mtg_processed_data.csv", sep = ",", encoding = "utf-8", index = False, header = True)


