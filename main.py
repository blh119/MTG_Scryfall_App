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
    game_formats = constants.GAME_FORMATS,
    non_legal_sets = constants.NON_LEGAL_MAGIC_SETS,
    basic_lands = constants.BASIC_LAND_TYPES,
    card_layout_keep = constants.CARD_LAYOUT_KEEP,
    color_pips_dict = constants.COLOR_PIPS_DICT,
    rarity = constants.RARITY,
    drop_columns = constants.DROP_COLUMNS,
    battle_attributes = constants.BATTLE_ATTRIBUTES,
    scryfall_supertypes_url = constants.SCRYFALL_SUPERTYPES_URL,
    scryfall_card_types_url = constants.SCRYFALL_CARD_TYPES_URL,
    scryfall_artifact_types_url = constants.SCRYFALL_ARTIFACT_TYPES_URL,
    scryfall_creature_types_url = constants.SCRYFALL_CREATURE_TYPES_URL,
    scryfall_enchantment_types_url = constants.SCRYFALL_ENCHANTMENT_TYPES_URL,
    scryfall_land_types_url = constants.SCRYFALL_LAND_TYPES_URL,
    scryfall_planeswalker_types_url = constants.SCRYFALL_PLANESWALKER_TYPES_URL,
    scryfall_spell_types_url = constants.SCRYFALL_SPELL_TYPES_URL,
    scryfall_keyword_abilities_url = constants.SCRYFALL_KEYWORD_ABILITIES_URL,
    scryfall_keyword_actions_url = constants.SCRYFALL_KEYWORD_ACTIONS_URL,
    scryfall_ability_words_url = constants.SCRYFALL_ABILITY_WORDS_URL
    
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

