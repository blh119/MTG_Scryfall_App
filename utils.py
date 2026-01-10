# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 23:14:41 2025

@author: holli
"""
import requests
import pandas as pd
import numpy as np
import re
import nltk
import matplotlib.pyplot as plt
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
nltk.download("punkt", force = True)

class MTGDataProcessor:
    
    def __init__(self, selected_columns, colors_dict, game_formats,
                 non_legal_sets, basic_lands, card_layout_keep, color_pips_dict, 
                 rarity, drop_columns, battle_attributes, scryfall_supertypes_url,scryfall_card_types_url, scryfall_artifact_types_url, scryfall_creature_types_url,
                 scryfall_enchantment_types_url, scryfall_land_types_url, scryfall_planeswalker_types_url,
                 scryfall_spell_types_url, scryfall_keyword_abilities_url, scryfall_keyword_actions_url, scryfall_ability_words_url,
                 scryfall_cards_url):
        
        self.selected_columns = selected_columns
        self.colors_dict = colors_dict
        self.game_formats = game_formats
        self.non_legal_sets = non_legal_sets
        self.basic_lands = basic_lands
        self.card_layout_keep = card_layout_keep
        self.color_pips_dict = color_pips_dict
        self.rarity = rarity
        self.drop_columns = drop_columns
        self.battle_attributes = battle_attributes
        self.scryfall_cards_url = scryfall_cards_url
        self.scryfall_urls = {"supertypes" : scryfall_supertypes_url,
                              "card_types" : scryfall_card_types_url,
                              "artifact_types" : scryfall_artifact_types_url,
                              "creature_types" : scryfall_creature_types_url,
                              "enchantment_types" : scryfall_enchantment_types_url,
                              "land_types" : scryfall_land_types_url,
                              "planeswalker_types" : scryfall_planeswalker_types_url,
                              "spell_types" : scryfall_spell_types_url,
                              "keyword_abilities" : scryfall_keyword_abilities_url,
                              "keyword_actions" : scryfall_keyword_actions_url,
                              "ability_words" : scryfall_ability_words_url}
        self.scryfall_features_lists = {}
        
        self.df = None
        
    def get_url_data(self, url):

        request_response = requests.get(url)
        
        if request_response.status_code == 200:
            
            return request_response.json()
        
        else:
            
            return request_response.status_code
    
    def json_to_dataframe(self, json_data):
        
        if isinstance(json_data, list):
            
            return pd.DataFrame(json_data)
        
        elif isinstance(json_data, dict):
            
            return pd.DataFrame([json_data])
        
        else:
            
            return pd.DataFrame([json_data])
    
    def load_data(self, url, to_list = False, to_dataframe = False):
        
        if to_dataframe and to_list == False:
            
            json_data = self.get_url_data(url) 
            return self.json_to_dataframe(json_data)
        
        elif to_dataframe == False and to_list:
            
            json_data = self.get_url_data(url)
            return self.json_to_list(json_data)
        
        elif to_dataframe and to_list:
            
            raise ValueError("Must either specify to_dataframe == False or to_list == False.\nOne must be true, while the other is false")
            
        else:
            
            raise ValueError("Must specify to_dataframe == True or to_list == True.\nOne must be true, while the other is false")
            
    def json_to_list(self, json_data):
        
        if isinstance(json_data, list):
            
            return [json_data]
        
        elif isinstance(json_data, dict):
            
            return json_data["data"]
        
        else:
            
            return [json_data]
    
    def get_scryfall_cards(self):
        
        self.df = self.load_data(self.scryfall_cards_url, to_dataframe = True)
        
    def get_scryfall_lists(self):
        
        for feature_type, url in self.scryfall_urls.items():
            current_list = self.load_data(url, to_list = True)
            self.scryfall_features_lists[feature_type] = current_list
            
    def filter_tokens_and_basic_lands(self):
        
        self.df = self.df.loc[:, self.selected_columns].copy()

        # Filter for English only cards and non tokens and digital only and filter out basic lands
        self.df = self.df.loc[(self.df.layout.isin(self.card_layout_keep)) &
                                ~(self.df.name.isin(self.basic_lands)) &
                                ~(self.df.set_name.isin(self.non_legal_sets)) &
                                (self.df["digital"] == False)].copy()
        
    def filter_for_first_printings(self):
        
        self.df = self.df.loc[~self.df["oracle_id"].isna(), ].copy() # first printing of any card
        self.df["type_line"] = self.df["type_line"].fillna("")
        
        self.df = self.df.sort_values(by = ["oracle_id", "card_name", "release_at"], ascending = [True, True])
        self.df = self.df.groupby(["oracle_id"]).head(1).reset_index(drop = True)
        
         
    def clean_power_and_toughness(self):
        
        for combat_stat in ["power", "toughness"]:
            
            combat_stat_series = self.df[combat_stat].astype(str)
            
            nan_mask = self.df[combat_stat].isna()
            inf_stat_mask = combat_stat_series.str.contains(r"\*", na = False)
            fixed_combat_mask = ~nan_mask & ~inf_stat_mask
            
            self.df.loc[nan_mask, combat_stat] = None
            self.df.loc[inf_stat_mask, combat_stat] = np.inf
            self.df.loc[fixed_combat_mask, combat_stat] = combat_stat_series[fixed_combat_mask]
            self.df[combat_stat] = self.df[combat_stat].astype("float64")
        
    def is_color(self):
        
        card_colors = pd.Series(["_".join(item) for item in self.df["color_identity"]])
        produced_mana_colors = self.df["produced_mana"].fillna("")
        produced_mana_colors = pd.Series(["_".join(item) for item in produced_mana_colors])
        
        
        for color, color_char in self.colors_dict.items():
        
            if color in ["blue", "red", "white", "black", "green", "tap", "colorless"]:
                
                self.df.loc[:, f"is_{color}"] = card_colors.str.contains(
                    
                    color_char, na = False
                    
                )
                
                self.df.loc[self.df["color_identity"].isna(), f"is_{color}"] = None
                self.df[f"is_{color}"] = self.df[f"is_{color}"].astype("boolean")
                
                self.df.loc[:, f"produced_{color}"] = produced_mana_colors.str.contains(
                    
                    color_char, na = False
                    
                )
                
                self.df.loc[self.df["produced_mana"].isna(), f"produced_{color}"] = None
                self.df[f"producd_{color}"] = self.df[f"produced_{color}"].astype("boolean")
            
            else:  # This is for colorless
            
                self.df.loc[:, f"is_{color}"] = card_colors == ""
                self.df.loc[self.df["color_identity"].isna(), f"is_{color}"] = None
                self.df[f"is_{color}"] = self.df[f"is_{color}"].astype("boolean")
                
                self.df.loc[:, f"produced_{color}"] = produced_mana_colors.str.contains(
                    
                    color_char, na = False
                    
                    )
                

                self.df.loc[self.df["produced_mana"].isna(), f"produced_{color}"] = None
                self.df[f"producd_{color}"] = self.df[f"produced_{color}"].astype("boolean")
                
    def is_in_format(self):
        
        self.df = pd.concat([self.df,
                             (pd.json_normalize(self.df["legalities"]))],
                               axis = 1,
                               ignore_index = False).reset_index(drop = True)
        
        all_games = pd.Series(["_".join(item) for item in self.df["games"]])
        unique_games = np.unique([item for current_list in self.df["games"] for item in current_list])
        
        for current_game in unique_games:   
            
            self.df[f"is_in_{current_game}"] = all_games.str.contains(
                
                current_game, na = False
                
            )
            
            self.df.loc[self.df["games"].isna(), f"is_in_{current_game}"] = None
            self.df[f"is_in_{current_game}"] = self.df[f"is_in_{current_game}"].astype("boolean")
            
    def is_supertype(self):
        
        self.df["type_line"] = self.df["type_line"].astype(str)
        
        for supertype in self.scryfall_features_lists["supertypes"]:
            
            self.df[f"is_{supertype}"] = self.df["type_line"].str.contains(supertype, case = False, regex = True)
            
    def is_card_type(self):
        
        for card_type in self.scryfall_features_lists["card_types"]:
            
            self.df[f"is_{card_type}"] = self.df["type_line"].str.contains(card_type, case = False, regex = True)
            
    def is_artifact_type(self):
        
        for artifact_type in self.scryfall_features_lists["artifact_types"]:
            
            self.df[f"is_{artifact_type}"] = self.df["type_line"].str.contains(artifact_type, case = False, regex = True)
            
    def is_creature_type(self):
        
        for creature_type in self.scryfall_features_lists["creature_types"]:
            
            self.df[f"is_{creature_type}"] = self.df["type_line"].str.contains(creature_type, case = False, regex = True)
            
    def is_enchantment_type(self):
        
        for enchantment_type in self.scryfall_features_lists["enchantment_types"]:
            
            self.df[f"is_{enchantment_type}"] = self.df["type_line"].str.contains(enchantment_type, case = False, regex = True)
            
            
    def is_land_type(self):
        
        for land_type in self.scryfall_features_lists["land_types"]:
            
            self.df[f"is_{land_type}"] = self.df["type_line"].str.contains(land_type, case = False, regex = True)
            
    def is_planeswalker_type(self):
        
        for planeswalker_type in self.scryfall_features_lists["planeswalker_types"]:
            
            self.df["is_{planeswalker_type}"] = self.df["type_line"].str.contains(planeswalker_type, case = False, regex = True)
            
    def is_spell_type(self):
        
        for spell_type in self.scryfall_features_lists["spell_types"]:
            
            self.df["is_{spell_type}"] = self.df["type_line"].str.contains(spell_type, case = False, regex = True)
            
    def has_keyword_abiliity(self):
        
        keyword_list = pd.Series(["_".join(item) for item in self.df["keyword"]])
        
        for keyword_ability in self.scryfall_features_lists["keyword_abilities"]:
            
            self.df["has_{keyword_ability}"] = keyword_list.str.contains(keyword_ability, case = False, regex = True)
            
    def has_keyword_action(self):
        
        for keyword_action in self.scryfall_features_lists["keyword_actions"]:
            
            self.df["has_{keyword_action}"] = self.df["oracle_text"].str.contains(keyword_action, case = False, regex = True)
    
    def has_ability_word(self):
        
        for ability_word in self.scryfall_features_lists["ability_words"]:
            
            self.df["has_{ability_word}"] = self.df["oracle_text"].str.contains(ability_word, case = False, regex = True)
            
    def get_rarity(self):
        
        for rarity_level in self.rarity:
            # Start with all NA
            self.df[f"is_{rarity_level}"] = None
        
            # Set True where rarity matches
            self.df.loc[self.df["rarity"] == rarity_level, f"is_{rarity_level}"] = True
        
            # Set False where rarity exists but doesn't match
            not_na_mask = self.df["rarity"].notna()
            not_match_mask = self.df["rarity"] != rarity_level
            self.df.loc[not_na_mask & not_match_mask, f"is_{rarity_level}"] = False
        
            # Ensure boolean type
            self.df[f"is_{rarity_level}"] = self.df[f"is_{rarity_level}"].astype("boolean")
        
    def create_legalities(self):  

        
        for game in self.game_formats:
            
            game_string = "_".join([game, "legal"])
            
            self.df[game_string] = None
            
            self.df.loc[self.df[game] == "legal", game_string] = True
            self.df.loc[self.df[game] == "not_legal", game_string] = False
            self.df.loc[self.df[game] == "banned", game_string] = False
            
            self.df.loc[self.df[game].isna(), game_string] = None
        
    def count_number_of_color_pips(self):
        
        mana_cost_list = self.df["mana_cost"].astype(str)

        self.df["mana_cost"] = mana_cost_list.str.replace(r"[{}]", "", regex = True)
        
        # keep as lambda function since it is well defined
        for color, color_char in self.color_pips_dict.items():
            
            self.df[f"{color}_pips"] = self.df["mana_cost"].apply(lambda x: len(re.findall(re.escape(color_char), str(x))))
            
        self.df["generic_pips"] = self.df["mana_cost"].apply(lambda x: sum(int(d) for d in re.findall(r"\d+", str(x))))
        
        mana_cost_list = self.df["mana_cost"].astype(str)
        generic_pip_list = self.df["generic_pips"]
        
        inf_stat_mask = generic_pip_list.str.contains(r"X", case = False, regex = True)
        nan_mask = generic_pip_list.isna()
        
        self.df.loc[inf_stat_mask, "generic_pips"] = np.inf
        self.df.loc[nan_mask, "generic_pips"] = None
        
        generic_pip_number_mask = ~inf_stat_mask & ~nan_mask
        self.df[generic_pip_number_mask, "generic_pips"] = generic_pip_list[generic_pip_number_mask]
        
        self.df["total_pips"] = (self.df["generic_pips"] +
                                 self.df["blue_pips"] +
                                 self.df["red_pips"] +
                                 self.df["black_pips"] +
                                 self.df["white_pips"] +
                                 self.df["green_pips"] +
                                 self.df["colorless_pips"])
        
    def planeswalker_loyalty(self):
        
        planeswalker_loyalty_list = pd.Series(self.df["planeswalker_loyalty"].astype(str))
        
        inf_stat_mask = planeswalker_loyalty_list.str.contains(r"\X", regex = True, case = False)
        number_mask = planeswalker_loyalty_list.str.contains(r"\d+", regex = True, case = False)
        nan_mask = ~inf_stat_mask & ~number_mask
        
        self.df.loc[inf_stat_mask, "planeswalker_loyalty"] = np.inf
        self.df.loc[nan_mask, "planeswalker_loyalty"] =  None
        self.df.loc[number_mask, "planeswalker_loyalty"] = planeswalker_loyalty_list[number_mask].copy().astype("int64")
        

    def get_number_of_splits(self, column_name):
        
        self.df["number_of_splits"] = self.df[column_name].apply(
            
            lambda x: len(re.findall(pattern = r"//", string = str(x))),
            
        )
        
        return max(self.df["number_of_splits"]) + 1
    
    def split_types(self):
            
        colnames_to_split = ["card_name", "mana_cost", "type_line"]        
        self.df = self.df.rename(columns = {"name" : "card_name"})
        
        for col_name in colnames_to_split:
            
            number_of_splits = self.get_number_of_splits(col_name)
            
            number_of_splits_list = [f"{col_name}-{i}" for i in range(1, number_of_splits + 1)]
                
            df_split = self.df[col_name].str.split("//", expand = True)
            df_split.columns = number_of_splits_list
            
            self.df = pd.concat([self.df, df_split], axis = 1).reset_index(drop = True)
            
        self.df = self.df.drop(colnames_to_split, axis = 1)

        
    def pivot_longer_double_cards(self):
        
        pivot_columns = self.df.columns[self.df.columns.str.contains(
            
            "card_name-\d+|mana_cost-\d+|type_line-\d+")].tolist()
        
        pivot_columns = list(set([re.sub(pattern = r"-\d+", string = col, repl = "") for col in pivot_columns]))
        
        self.df = pd.wide_to_long(self.df, pivot_columns, i = "id", j = "card_sub", sep = "-")
        
        self.df = self.df.reset_index(drop = True)
        
    def drop_non_legal_cards(self):
        
        legal_columns = [current_col for current_col in self.df.columns if bool(re.search(pattern = r"_legal$",
                                                                                           string = current_col))]
        
        temp = self.df[legal_columns]
        temp = temp.fillna(False).astype(int)
        
        self.df["legal_sum"] = temp.sum(axis = 1)
        
        self.df = self.df[self.df["legal_sum"] != 0].copy()
        
    def drop_unnecessary_columns(self):
        
        self.df = self.df.drop(self.drop_columns, axis = 1)
        self.df.columns = [current_col.lower() for current_col in self.df.columns]
        
    def one_hot_encode_features(self):
        
        self.is_supertype()
        self.is_card_type()
        self.is_artifact_type()
        self.is_creature_type()
        self.is_enchantment_type()
        self.is_land_type()
        self.is_planeswalker_type()
        self.is_spell_type()
        self.has_keyword_abiliity()
        self.has_keyword_action()
        self.has_ability_word()
        
    def process_data(self):
        
        if self.df is None:
            
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.filter_tokens_and_basic_lands()
        self.pivot_longer_double_cards()
        self.filter_for_first_printings()
        self.one_hot_encode_features()
        self.get_rarity()
        self.create_legalities()
        self.count_number_of_color_pips()
        self.drop_non_legal_cards()
        self.clean_power_and_toughness()
        self.planeswalker_loyalty()
        self.drop_unnecessary_columns()
        
class CardRecommenderModel:
    
    def __init__(self, data_processor, stopwords):
        
        self.data_processor = data_processor
        self.stopwords = stopwords
        self.orcale_text_model = None 
        self.keyword_text_model = None 
        self.valid_game_format = None
                    
    def legal_cards_for_format(self, game_format = "Commander"):

        self.valid_game_format = game_format.strip().lower()

        if self.valid_game_format in self.data_processor.game_formats:
            
            self.data_processor.df = self.data_processor.df[self.data_processor.df[f"{self.valid_game_format}_legal"] == True].reset_index(drop = True)
        else:

            raise ValueError("Attempting to pass non-legal game format")
    
    def tokenize_text(self):
        
        self.data_processor.df["oracle_text_tokens"] = self.data_processor.df["oracle_text"].apply(self.tokenize_words)
        self.data_processor.df["keywords_string_tokens"] = self.data_processor.df["keywords_string"].apply(self.tokenize_words)
        self.data_processor.df["card_name_tokens"] = self.data_processor.df["card_name"].apply(self.tokenize_words)
        self.data_processor.df["card_subtype_tokens"] = self.data_processor.df["card_subtype"].apply(self.tokenize_words)
        
    def tokenize_words(self, text):
        
        if not text or pd.isna(text):
            
            return []
        
        else: 
            
            token = word_tokenize(text.lower()) 
            filtered_token = [word for word in token if word not in self.stopwords] 
            return filtered_token
        
    def trainWord2Vec_model(self):

        self.oracle_text_model = Word2Vec(sentences = self.data_processor.df["oracle_text_tokens"],
                                          vector_size = 100,
                                          window = 5, 
                                          min_count = 1, 
                                          workers = 4,
                                          seed = 99)
        
        self.keywords_string_model = Word2Vec(sentences = self.data_processor.df["keywords_string_tokens"],
                                            vector_size = 50,
                                            window = 5, 
         t                                   min_count = 1, 
                                            workers = 4,
                                            seed = 99)
        
        self.card_name_model = Word2Vec(sentences = self.data_processor.df["card_name_tokens"],
                                             vector_size = 40,
                                             window = 5, 
                                             min_count = 1, 
                                             workers = 4,
                                             seed = 99)
        
        self.card_subtype_model = Word2Vec(sentences = self.data_processor.df["card_subtype_tokens"],
                                           vector_size = 40,
                                           window = 5,
                                           min_count = 1,
                                           workers = 4,
                                           seed = 99)
        
    def average_word_vector_to_df(self):
        
        self.data_processor.df["oracle_text_avg_vec"] = self.data_processor.df["oracle_text_tokens"].apply(
            
            lambda x: self.get_average_word_vector(self.oracle_text_model, x)
            
            )
        
        self.data_processor.df["keywords_string_avg_vec"] = self.data_processor.df["keywords_string_tokens"].apply(
            
            lambda x: self.get_average_word_vector(self.keywords_string_model, x)
            
            )
        
        self.data_processor.df["card_name_avg_vec"] = self.data_processor.df["card_name_tokens"].apply(
            
            lambda x: self.get_average_word_vector(self.card_name_model, x)
            
            )
        
        self.data_processor.df["card_subtype_avg_vec"] = self.data_processor.df["card_subtype_tokens"].apply(
            
            lambda x: self.get_average_word_vector(self.card_subtype_model, x)
            
            )
        
    def get_average_word_vector(self, model, text_vec):
        
        if text_vec == []:
            
            return np.zeros(model.vector_size)
        
        else: 
            
            word_vec = [model.wv[word] for word in text_vec if word in model.wv.key_to_index] 
            
            if word_vec:
                
                return np.mean(word_vec, axis = 0)
            
            else:
                
                return np.zeros(model.vector_size)
    
    def get_model_inputs(self):
        
        # color columns
        is_color = ["is_" + color for color in list(self.data_processor.colors_dict)]
        produced_color = ["produced_" + color for color in list(self.data_processor.colors_dict)]
        
        color_pips = [color + "_pips" for color in list(self.data_processor.colors_dict)]
        
        primary_card_type = ["is_" + card_type.lower() for card_type in self.data_processor.card_types]
        secondary_card_type = ["is_" + card_subtype.lower() for card_subtype in self.data_processor.card_subtypes]
        
        rarity_type = ["is_" + rarity.lower() for rarity in self.data_processor.rarity]
        
        battle_attributes_type = self.data_processor.battle_attributes
        
        color_type_features = is_color + produced_color
        
        self.standardscaler = StandardScaler()
        
        self.color_type_features = self.data_processor.df[color_type_features].fillna(False).astype(int).values
        
        self.color_pips_features = self.data_processor.df[color_pips].fillna(0).values
        self.color_pips_features = np.nan_to_num(x = self.color_pips_features,
                                                 nan = -1,
                                                 posinf = 1e6,
                                                 neginf = -1e6)
        
        self.color_pips_features = self.standardscaler.fit_transform(self.color_pips_features)
        
        self.color_features = np.hstack([self.color_type_features, 
                                         self.color_pips_features])
        
        self.primary_card_type_features = self.data_processor.df[primary_card_type].fillna(False).astype(int).values
        self.secondary_card_type_features = self.data_processor.df[secondary_card_type].fillna(False).astype(int).values
        
        self.rarity_features = self.data_processor.df[rarity_type].fillna(False).astype(int).values
        
        self.battle_features = self.data_processor.df[battle_attributes_type].values
        self.battle_features = np.nan_to_num(x = self.battle_features,
                                             nan = -1,
                                             posinf = 1e6,
                                             neginf = -1e6)
        
        self.battle_features = self.standardscaler.fit_transform(self.battle_features)
        
        # oracle_features
        self.oracle_features = np.stack(self.data_processor.df["oracle_text_avg_vec"].values, axis = 0)
        self.oracle_features = self.standardscaler.fit_transform(self.oracle_features)
        
        # keyword features
        self.keyword_features = np.stack(self.data_processor.df["keywords_string_avg_vec"].values, axis = 0)
        self.keyword_features = self.standardscaler.fit_transform(self.keyword_features)
        
        # card name features
        self.card_name_features = np.stack(self.data_processor.df["card_name_avg_vec"].values, axis = 0)
        self.card_name_features = self.standardscaler.fit_transform(self.card_name_features)
        
        # card subtype features
        self.card_subtype_features = np.stack(self.data_processor.df["card_subtype_avg_vec"].values, axis = 0)
        self.card_subtype_features = self.standardscaler.fit_transform(self.card_subtype_features)
        
        self.binary_features = np.hstack([self.color_type_features,
                                          self.primary_card_type_features,
                                          self.secondary_card_type_features,
                                          self.rarity_features])
        
        self.numerical_features = np.hstack([self.color_pips_features, 
                                             self.battle_features])

        self.model_features = np.concatenate([self.binary_features,
                                              self.numerical_features,
                                              self.oracle_features,
                                              self.keyword_features,
                                              self.card_subtype_features,
                                              self.card_name_features],
                                              axis = 1)
        
        self.scaled_model_features = np.concatenate([self.binary_features * .2,
                                                     self.numerical_features * .1,
                                                     self.oracle_features * .3,
                                                     self.keyword_features * .1,
                                                     self.card_subtype_features * .15,
                                                     self.card_name_features * .15],
                                                     axis = 1)
        
        self.feature_names = (color_type_features +  primary_card_type +
                              secondary_card_type + rarity_type + 
                              color_pips + battle_attributes_type +
                              [f"ocacle_feature_{i}" for i in range(1, 101)] +
                              [f"keyword_feature_{i}" for i in range(1, 51)] + 
                              [f"card_subtype_features{i}" for i in range(1, 41)] +
                              [f"card_name_feature_{i}" for i in range(1, 41)])

        
    def train_KNN_model(self, neighbors = 6, n_features = 50):
        
        self.pca_model = PCA(n_components = n_features, random_state = 99)  # Reduce dimensions significantly
        self.scaled_model_features_pca = self.pca_model.fit_transform(self.scaled_model_features)
        self.unscaled_model_features_pca = self.pca_model.fit_transform(self.model_features)
        
        self.knn_model_scaled = NearestNeighbors(n_neighbors = neighbors, algorithm = "ball_tree").fit(self.scaled_model_features_pca)
        self.knn_model_unscaled = NearestNeighbors(n_neighbors = neighbors, algorithm = "ball_tree").fit(self.unscaled_model_features_pca)
    
    def find_nearest_neighbor_scaled(self, user_card_name):
        
        user_card_name = user_card_name.lower().strip()
        
        card_match = self.data_processor.df[self.data_processor.df["card_name"].str.lower() == user_card_name]
        
        if card_match.empty:
            
            print(f"{user_card_name} not found")
            return None

        input_card_index = self.data_processor.df[self.data_processor.df["card_name"].str.lower() == user_card_name].index[0]
        input_card_features = self.scaled_model_features_pca[input_card_index].reshape(1, -1)
        
        distances, indices = self.knn_model_scaled.kneighbors(input_card_features)
        
        input_card_info = self.data_processor.df.iloc[input_card_index, :]
        
        print(f"\nInput Card: {input_card_info['card_name']}")
        print(f"\nCard Type: {input_card_info['card_type']}")
        print(f"\nMana Cost: {input_card_info.get('mana_cost', 'No Mana Cost')}")
        print(f"\nOracle Text: {input_card_info.get('oracle_text', 'No Oracle Text')}")
        print("\n" + "=" * 60)
        print("RECOMMENDED CARDS")
        
        recommendations_data = self.data_processor.df.loc[indices[0], ].reset_index()
        recommendations_data = recommendations_data.iloc[1: ]
        
        for index, row in recommendations_data.iterrows():
            
            print(f"\nRecommended Card {index}: {row['card_name']}")
            print(f"\nCard Type {index}: {row['card_type']}")
            print(f"\nMana Cost: {index}: {row['mana_cost']}")
            print(f"\nOracle Text: {index}: {row['oracle_text']}")
            print("\n" + "=" * 60)

    def find_nearest_neighbor_unscaled(self, user_card_name):
        
        user_card_name = user_card_name.lower().strip()
        
        card_match = self.data_processor.df[self.data_processor.df["card_name"].str.lower() == user_card_name]
        
        if card_match.empty:
            
            print(f"{user_card_name} not found")
            return None

        input_card_index = self.data_processor.df[self.data_processor.df["card_name"].str.lower() == user_card_name].index[0]
        input_card_features = self.unscaled_model_features_pca[input_card_index].reshape(1, -1)
        
        distances, indices = self.knn_model_unscaled.kneighbors(input_card_features)
        
        input_card_info = self.data_processor.df.iloc[input_card_index, :]
        
        print(f"\nInput Card: {input_card_info['card_name']}")
        print(f"\nCard Type: {input_card_info['card_type']}")
        print(f"\nMana Cost: {input_card_info.get('mana_cost', 'No Mana Cost')}")
        print(f"\nOracle Text: {input_card_info.get('oracle_text', 'No Oracle Text')}")
        print("\n" + "=" * 60)
        print("RECOMMENDED CARDS")
        
        recommendations_data = self.data_processor.df.loc[indices[0], ].reset_index()
        recommendations_data = recommendations_data.iloc[1: ]
        
        for index, row in recommendations_data.iterrows():
            
            print(f"\nRecommended Card {index}: {row['card_name']}")
            print(f"\nCard Type {index}: {row['card_type']}")
            print(f"\nMana Cost: {index}: {row['mana_cost']}")
            print(f"\nOracle Text: {index}: {row['oracle_text']}")
            print("\n" + "=" * 60)
        
    def train_kmeans_model(self, n_clusters = 8):
        
        self.kmeans_model = KMeans(n_clusters = n_clusters, random_state = 99)
        self.cluster_names = self.kmeans_model.fit_predict(self.unscaled_model_features_pca)
        
    def train_tsne(self, n_components = 2):
        
        self.tsne_model = TSNE(n_components = n_components, random_state = 99)
        self.tsne_features = self.tsne_model.fit_transform(self.unscaled_model_features_pca)
        
    def analyze_clusters(self):
        
        self.data_processor.df["cluster"] = self.cluster_names
        
        self.card_type_by_cluster = self.data_processor.df.groupby("cluster")["card_type"].value_counts().reset_index()
        self.card_type_by_cluster = self.card_type_by_cluster.sort_values(by = ["cluster", "count"], ascending = [True, False])
        self.card_type_by_cluster = self.card_type_by_cluster.groupby("cluster").head(5).reset_index(drop = True)
        
        self.card_subtype_by_cluster = self.data_processor.df.groupby("cluster")["card_subtype"].value_counts().reset_index()
        self.card_subtype_by_cluster = self.card_subtype_by_cluster.sort_values(by = ["cluster", "count"], ascending = [True, False])
        self.card_subtype_by_cluster = self.card_subtype_by_cluster.groupby("cluster").head(5).reset_index(drop = True)

        self.color_by_cluster = self.data_processor.df.groupby("cluster").agg({
            
            "is_blue" : "sum",
            "is_red" : "sum",
            "is_black" : "sum",
            "is_green" : "sum",
            "is_white" : "sum",
            "is_colorless" : "sum"
            
        }).reset_index(drop = False)

    def RandomForest_for_clusters(self):

        X = self.model_features
        y = self.cluster_names

        self.rf_cluster_model = RandomForestClassifier(n_estimators = 100, random_state = 99)
        self.rf_cluster_model.fit(X, y)

    def train_models(self):

        self.legal_cards_for_format()
        self.tokenize_text()
        self.trainWord2Vec_model()
        self.average_word_vector_to_df()
        self.get_model_inputs()
        self.train_KNN_model()
        self.train_kmeans_model()
        self.RandomForest_for_clusters()

class DataVisuals:
    
    def __init__(self, card_rec_model):
        
        self.card_rec_model = card_rec_model
        
    def random_forest_feature_importance_visualization(self):

        self.rf_cluster_model_feature_importance = self.card_rec_model.rf_cluster_model.feature_importances_

        indices = np.argsort(self.rf_cluster_model_feature_importance)[::-1][:20]
        plt.figure(figsize = (12, 6))
        self.feature_importance_bar_graph = plt.barh(range(20), self.rf_cluster_model_feature_importance[indices])
        plt.yticks(range(20), [self.feature_names[i] for i in indices])
        plt.xlabel("Feature Importance")
        plt.title("Feature Importance for Card Recommender Model")
        plt.tight_layout()
        plt.show()
        
    def tsne_data_visualization(self, n_components = 2):
        
        plt.figure(figsize = (12, 8))

        for cluster in np.unique(self.card_rec_model.cluster_names):

            cluster_mask = self.card_rec_model.cluster_names == cluster
            
            self.tsne_scatter = plt.scatter(self.card_rec_model.tsne_features[cluster_mask, 0], 
                                            self.card_rec_model.tsne_features[cluster_mask, 1],
                                            label = f"Cluster {cluster}")
        
        plt.title("MTG Cards Clusters by K-Means")
        plt.xlabel("t-SNE Component 1")
        plt.ylabel("t-SNE Component 2")
        plt.legend()
        
        # add a few card names to the plot
        sample_card_data = self.card_rec_model.data_processor.df.sample(25, replace = False)
        sample_card_indices = sample_card_data.index.tolist()
        
        for index in sample_card_indices:
            
            plt.annotate(self.card_rec_model.data_processor.df.loc[index, "card_name"],
                         (self.card_rec_model.tsne_features[index, 0], 
                          self.card_rec_model.tsne_features[index, 1]))
            
        plt.tight_layout()
        plt.show()

    def plot_card_type_clusters(self):

        cluster = 0

        fig, axs = plt.subplots(2, 4, figsize = (15, 15))
        fig.suptitle("Most Common Card Type by Cluster")

        for i in range(2):
            for j in range(4):

                cluster_mask = self.card_rec_model.card_type_by_cluster["cluster"] == cluster
                cluster_values = self.card_rec_model.card_type_by_cluster.loc[cluster_mask]
            
                axs[i, j].bar(cluster_values["card_type"], cluster_values["count"])
                axs[i, j].set_title(f"Cluster {cluster} Most Common Card Type")
                axs[i, j].set_xticklabels(cluster_values["card_type"], rotation = 90)
                axs[i, j].set_ylabel("Count")

                cluster = cluster + 1

        fig.tight_layout()
        plt.show()

    def plot_card_subtype_clusters(self):

        cluster = 0

        fig, axs = plt.subplots(2, 4, figsize = (15, 15))
        fig.suptitle("Most Common Card Subtype by Cluster")

        for i in range(2):
            for j in range(4):

                cluster_mask = self.card_rec_model.card_subtype_by_cluster["cluster"] == cluster
                cluster_values = self.card_rec_model.card_subtype_by_cluster.loc[cluster_mask]
            
                axs[i, j].bar(cluster_values["card_subtype"], cluster_values["count"])
                axs[i, j].set_title(f"Cluster {cluster} Most Common Card Subtype")
                axs[i, j].set_xticklabels(cluster_values["card_subtype"], rotation = 90)
                axs[i, j].set_ylabel("Count")

                cluster = cluster + 1

        fig.tight_layout()
        plt.show()

    def plot_color_by_cluster(self):

        cluster = 0

        fig, axs = plt.subplots(2, 4, figsize = (15, 15))
        fig.suptitle("Card Color by Cluster")

        for i in range(2):
            for j in range(4):

                cluster_mask = self.card_rec_model.color_by_cluster["cluster"] == cluster
                cluster_values = self.card_rec_model.color_by_cluster.loc[cluster_mask]

                total_blue = cluster_values["is_blue"].sum()
                total_red = cluster_values["is_red"].sum()
                total_black = cluster_values["is_black"].sum()
                total_white = cluster_values["is_white"].sum()
                total_green = cluster_values["is_green"].sum()
                total_colorless = cluster_values["is_colorless"].sum()

                color_totals = np.array([total_blue, total_red, total_black, total_white, total_green, total_colorless])
                color_names = np.array(["blue", "red", "black", "white", "green", "colorless"])
                
                axs[i, j].bar(color_names, color_totals)
                axs[i, j].set_title(f"Cluster {cluster}: Most Common Color by Cluster")
                axs[i, j].set_xticklabels(color_names, rotation = 90)
                axs[i, j].set_ylabel("Count")

                cluster = cluster + 1

        fig.tight_layout()
        plt.show()
           
class CardRecommnderUserInterface:
    
    def __init__(self, card_rec_model):
        
        self.card_rec_model = card_rec_model
        self.welcome_message = """Welcome to the MTG Card Recommender!
        
        We are here to recommend the best replacement for a card that you give us!
        
        Would you like us to give you a recommendation?(Y/N) """
        self.print_welcome_message()
        
        
    def print_welcome_message(self):
        
        print(self.welcome_message)
    
    def card_recommendation_from_user(self):
        
        self.print_welcome_message()
        
        self.does_the_user_want_a_rec = input().lower().strip()
        
        if self.does_the_user_want_a_rec in ["y", "yes"]:
            
            self.card_rec_loop()
        
        elif self.does_the_user_want_a_rec in ["n", "no"]:
            
            print("Thanks for using our recommendation tool!")
            print("Have a good day!")
        
        else:
            
            print(f"{self.does_the_user_want_a_rec} is not a valid response. Please enter: (Y/N)")
        
    def card_rec_loop(self):
        
        get_rec = True

        while get_rec:
            
            print("\n" + "="*60)
            print("Which card would you like a recommendation for?")
            user_card = input().lower().strip()
            
            try:
                
                self.card_rec_model.find_nearest_neighbor_unscaled(user_card)
            
            except Exception as e:
                
                print(f"Error getting recommendation: {e}")
                print("Please try another card.")
                continue
            
            while True:
                
                print("\nWould you like another recommendation? (Y/N)")
                self.does_the_user_want_a_rec = input().lower().strip()
                
                if self.does_the_user_want_a_rec in ["y", "yes"]:
                    
                    break # go back to the last loop
                    
                elif self.does_the_user_want_a_rec in ["n", "no"]:
                    
                    print("\n" + "="*60)
                    print("Thanks for using our recommendation tool!")
                    print("Have a good day!")
                    
                    get_rec = False
                    
                    break # break the loop
                
                else:
                
                    print(f"{self.does_the_user_want_a_rec} is not a valid response.")
                    print("Please enter Y or N")
        
        
        
        
        
    
        
        
        
        
        
        
        
        
        
        
        
                    
    
                
        
 
        
        
            
            
        
        
        
        
        
 
        
 
        
        
        
        
   
    
        
    
        
        
        
        
        
        
        
        
        
        
        
        
        
    
        
        
        
        
        
        
        
        
        
        
        
                    
    
                
        
 