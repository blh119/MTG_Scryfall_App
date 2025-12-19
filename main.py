# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 22:27:39 2025

@author: holli
"""
import constants
<<<<<<< HEAD
from utils import MTGDataProcessor, CardRecommenderModel, DataVisuals, CardRecommnderUserInterface
=======
from utils import MTGDataProcessor, CardRecommenderModel, DataVisuals
>>>>>>> fcbc44c27ef949b890f0900ba02da08d04b296b9

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

processor.load_data(constants.SCRYFALL_CARDS_URL)
processor.process_data()

card_training_model = CardRecommenderModel(processor)
card_training_model.train_models()

card_recommender_visuals = DataVisuals(card_training_model)



card_training_model.analyze_clusters()

card_training_model.plot_card_type_clusters()
card_training_model.plot_card_subtype_clusters()
card_training_model.plot_color_by_cluster()

card_training_model.tsne_data_visualization()
card_training_model.random_forest_feature_importance_visualization()

<<<<<<< HEAD


=======
>>>>>>> fcbc44c27ef949b890f0900ba02da08d04b296b9

