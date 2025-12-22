# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 22:27:39 2025

@author: holli
"""
import constants
from utils import MTGDataProcessor, CardRecommenderModel, DataVisuals, CardRecommnderUserInterface

processor = MTGDataProcessor(
    
    selected_columns = constants.SELECTED_COLUMNS,
    colors_dict = constants.COLORS_DICT,
    card_types = constants.CARD_TYPES,
    card_subtypes = constants.CARD_SUBTYPES,
    game_formats = constants.GAME_FORMATS,
    non_legal_sets = constants.NON_LEGAL_MAGIC_SETS,
    basic_lands = constants.BASIC_LAND_TYPES,
    card_layout_keep = constants.CARD_LAYOUT_KEEP,
    color_pips_dict = constants.COLOR_PIPS_DICT,
    rarity = constants.RARITY,
    drop_columns = constants.DROP_COLUMNS,
    battle_attributes = constants.BATTLE_ATTRIBUTES
)

# Data Cleaners
processor.load_data(constants.SCRYFALL_CARDS_URL)
processor.process_data()

# Train Models
card_training_model = CardRecommenderModel(processor, constants.STOPWORDS)
card_training_model.train_models()
card_training_model.analyze_clusters()

# Data Visuals
card_recommender_visuals = DataVisuals(card_training_model)
card_recommender_visuals.plot_card_type_clusters()
card_recommender_visuals.plot_card_subtype_clusters()
card_recommender_visuals.plot_color_by_cluster()
card_recommender_visuals.tsne_data_visualization()
card_recommender_visuals.random_forest_feature_importance_visualization()

card_recommender_user_interface = CardRecommnderUserInterface(card_training_model)
card_recommender_user_interface.card_recommendation_from_user()

