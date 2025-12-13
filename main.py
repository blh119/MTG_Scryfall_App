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
import nltk
import matplotlib.pyplot as plt
from gensim.models import Word2Vec
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
nltk.download("stopwords", force = True)
nltk.download("punkt", force = True)

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

card_training_model = CardRecommenderModel(processor)
card_training_model.train_models()

card_training_model.analyze_clusters()

card_training_model.plot_card_type_clusters()
card_training_model.plot_card_subtype_clusters()
card_training_model.plot_color_by_cluster()

card_training_model.tsne_data_visualization()
card_training_model.random_forest_feature_importance_visualization()


