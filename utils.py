# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 23:14:41 2025

@author: holli
"""
class MTGDataProcessor:
    
    def __init__(self, selected_columns, colors_dict, card_types, card_subtypes,
                 game_formats, non_legal_sets, basic_lands, card_layout_keep,
                 color_pips_dict, rarity, drop_columns, battle_attributes):
        
        self.selected_columns = selected_columns
        self.colors_dict = colors_dict
        self.card_types = card_types
        self.card_subtypes = card_subtypes
        self.game_formats = game_formats
        self.non_legal_sets = non_legal_sets
        self.basic_lands = basic_lands
        self.card_layout_keep = card_layout_keep
        self.color_pips_dict = color_pips_dict
        self.rarity = rarity
        self.drop_columns = drop_columns
        self.battle_attributes = battle_attributes
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
    
    def load_data(self, url):
        
        json_data = self.get_url_data(url)
        self.df = self.json_to_dataframe(json_data)
        
    
    def filter_tokens_and_basic_lands(self):
        
        df_clean = self.df.copy()
        
        df_clean = df_clean[self.selected_columns]

        # Filter for English only cards and non tokens and digital only and filter out basic lands
        df_clean = df_clean.loc[(df_clean.layout.isin(self.card_layout_keep)) &
                                ~(df_clean.name.isin(self.basic_lands)) &
                                ~(df_clean.set_name.isin(self.non_legal_sets)) &
                                (df_clean["digital"] == False)]
        self.df = df_clean
        
    def clean_combat_stat(self, value):
        
        if value is None or (isinstance(value, float) and np.isnan(value)):
            
            return None
        
        inf_stat = bool(re.search(pattern = r"\*", string = value))
        
        if inf_stat:
            
            return np.inf
        
        else:
            
            return int(value)
        
        
    def clean_power_and_toughness(self):
        
        df_clean = self.df.copy()
        
        df_clean["power"] = df_clean["power"].apply(self.clean_combat_stat)
        df_clean["toughness"] = df_clean["toughness"].apply(self.clean_combat_stat)
        
        self.df = df_clean
        
    def is_color(self):
    
        df_clean = self.df.copy()
        
        for color, color_char in self.colors_dict.items():
        
            if color in ["blue", "red", "white", "black", "green"]:

                df_clean.loc[:, f"is_{color}"] = df_clean["color_identity"].apply(
                    lambda x: color_char in x if isinstance(x, list) else False
                ).astype("boolean") 
            
                df_clean.loc[df_clean["color_identity"].isna(), f"is_{color}"] = None
            
                df_clean[f"produced_{color}"] = df_clean["produced_mana"].apply(
                lambda x: color_char in x if isinstance(x, list) else False
                ).astype("boolean")
            
                df_clean.loc[df_clean["produced_mana"].isna(), f"produced_{color}"] = None
            
            else:  # This is for colorless
            
                df_clean.loc[:, f"is_{color}"] = df_clean["color_identity"].apply(
                    lambda x: len(x) == 0 if isinstance(x, list) else False
                    ).astype("boolean")
            
                df_clean.loc[df_clean["color_identity"].isna(), f"is_{color}"] = None
            
                df_clean[f"produced_{color}"] = df_clean["produced_mana"].apply(
                    lambda x: "C" in x if isinstance(x, list) else False
                    ).astype("boolean")
            
                df_clean.loc[df_clean["produced_mana"].isna(), f"produced_{color}"] = None
            
        self.df = df_clean
        
    def is_in_format(self):
        
        df_clean = self.df.copy()
        
        df_clean = pd.concat([df_clean,
                              (df_clean["legalities"].apply(pd.Series))],
                               axis = 1,
                               ignore_index = False).reset_index(drop = True)
        
        all_games = set([game for sublist in df_clean["games"] for game in sublist])
        
        for current_game in all_games:
            
            df_clean[f"is_in_{current_game}"] = df_clean["games"].apply(
                
                lambda x: current_game in x if isinstance(x, list) else False
                
                ).astype("boolean")
            
            df_clean.loc[df_clean["games"].isna(), f"is_in_{current_game}"] = None
            
        self.df = df_clean
        
    
    def is_card_type(self):
        
        df_clean = self.df.copy()
        
        for card_type in self.card_types:
            
            has_card_type = df_clean["type_line"].str.contains(
                
                card_type, na = False, regex = True
                
            )
            
            df_clean[f"is_{card_type}"] = None
            df_clean.loc[has_card_type, f"is_{card_type}"] = True
            df_clean.loc[~has_card_type, f"is_{card_type}"] = False
            
            
        for card_subtype in self.card_subtypes:
            
            has_card_type = df_clean["type_line"].str.contains(
                
                card_subtype, na = False, regex = True
    
            )
            
            df_clean[f"is_{card_subtype}"] = None
            df_clean.loc[has_card_type, f"is_{card_subtype}"] = True
            df_clean.loc[~has_card_type, f"is_{card_subtype}"] = False
            
        self.df = df_clean
        
    def get_rarity(self):
        
        df_clean = self.df.copy()

        for rarity_level in self.rarity:
            # Start with all NA
            df_clean[f"is_{rarity_level}"] = None
        
            # Set True where rarity matches
            df_clean.loc[df_clean["rarity"] == rarity_level, f"is_{rarity_level}"] = True
        
            # Set False where rarity exists but doesn't match
            not_na_mask = df_clean["rarity"].notna()
            not_match_mask = df_clean["rarity"] != rarity_level
            df_clean.loc[not_na_mask & not_match_mask, f"is_{rarity_level}"] = False
        
            # Ensure boolean type
            df_clean[f"is_{rarity_level}"] = df_clean[f"is_{rarity_level}"].astype("boolean")
    
        self.df = df_clean
    
    def create_subtype(self):
        
        df_clean = self.df.copy()
        
        df_clean[["card_type", "card_subtype"]] = df_clean["type_line"].str.split(pat = "—", n = 1, expand = True)
        
        df_clean["card_type"] = df_clean["card_type"].str.strip()
        df_clean["card_subtype"] = df_clean["card_subtype"].str.strip()

        card_subtype_na_mask = df_clean["card_subtype"].isna()

        # fill na card_subtype with the main card_type
        df_clean["card_subtype"] = df_clean["card_subtype"].fillna(df_clean.loc[card_subtype_na_mask, "card_type"])
        
        self.df = df_clean
        
    def create_keyword_string(self):
        
        df_clean = self.df.copy()
        
        df_clean["keywords_string"] = df_clean["keywords"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) and len(x) > 0 else None)
        
        self.df = df_clean
        
    def create_legalities(self):  
        
        df_clean = self.df.copy()
        
        for game in self.game_formats:
            
            game_string = "_".join([game, "legal"])
            
            df_clean[game_string] = None
            
            df_clean.loc[df_clean[game] == "legal", game_string] = True
            df_clean.loc[df_clean[game] == "not_legal", game_string] = False
            df_clean.loc[df_clean[game] == "banned", game_string] = False
            
            df_clean.loc[df_clean[game].isna(), game_string] = None
        
        self.df = df_clean
        
    def count_number_of_color_pips(self):
        
        df_output = self.df.copy()
        
        df_output["mana_cost"] = df_output["mana_cost"].apply(lambda x: re.sub(pattern = r"[{}]",  repl = "", string = str(x)))
        
        for color, color_char in self.color_pips_dict.items():
            
            df_output[f"{color}_pips"] = df_output["mana_cost"].apply(lambda x: len(re.findall(re.escape(color_char), str(x))))
            
        df_output["generic_pips"] = df_output["mana_cost"].apply(lambda x: sum(int(d) for d in re.findall(r"\d+", str(x))))
        
        df_output["generic_pips"] = np.select(
            
            condlist = [df_output["mana_cost"].apply(lambda x: bool(re.search(r"X", str(x)))),
                        df_output["mana_cost"].isna()],
            choicelist = [np.inf, None],
            default = df_output["generic_pips"]
            
        )
        
        df_output["total_pips"] = (df_output["generic_pips"] +
                                   df_output["blue_pips"] +
                                   df_output["red_pips"] +
                                   df_output["black_pips"] +
                                   df_output["white_pips"] +
                                   df_output["green_pips"] +
                                   df_output["colorless_pips"])
        
        self.df = df_output
        
    def extract_planeswalker_loyalty(self, value): 
        
        if value is None or (isinstance(value, float) and np.isnan(value)):
        
            return None

        value = str(value)

        match = re.search(r"(\d+|X)", value)
        
        if match:
            
            token = match.group(1)
        
        if token == "X":
            
            return np.inf
        
        else:

            return int(token)

        return None
        
    def planeswalker_loyalty(self):
        
        df_clean = self.df.copy()

        df_clean["planeswalker_loyalty"] = df_clean["loyalty"].apply(self.extract_planeswalker_loyalty) 
        
        self.df = df_clean

    def get_number_of_splits(self, df, column_name):
        
        df_clean = df.copy()
        
        df_clean["number_of_splits"] = df_clean[column_name].apply(
            
            lambda x: len(re.findall(pattern = r"//", string = str(x))),
            
        )
        
        return max(df_clean["number_of_splits"]) + 1
    
    def split_types(self):
        
        df_clean = self.df.copy()
            
        colnames_to_split = ["card_name", "mana_cost", "type_line"]        
        df_clean = df_clean.rename(columns = {"name" : "card_name"})
        
        for col_name in colnames_to_split:
            
            number_of_splits = self.get_number_of_splits(df_clean, col_name)
            
            number_of_splits_list = [f"{col_name}-{i}" for i in range(1, number_of_splits + 1)]
                
            df_clean_split = df_clean[col_name].str.split("//", expand = True)
            df_clean_split.columns = number_of_splits_list
            
            df_clean = pd.concat([df_clean, df_clean_split], axis = 1).reset_index(drop = True)
            
        df_clean = df_clean.drop(colnames_to_split, axis = 1)
            
        self.df = df_clean
        
    def pivot_longer_double_cards(self):
        
        df_clean = self.df
        
        pivot_columns = df_clean.columns[df_clean.columns.str.contains(
            
            "card_name-\d+|mana_cost-\d+|type_line-\d+")].tolist()
        
        pivot_columns = list(set([re.sub(pattern = r"-\d+", string = col, repl = "") for col in pivot_columns]))
        
        df_clean = pd.wide_to_long(df_clean, pivot_columns, i = "id", 
                                   j = "card_sub", sep = "-")
        
        df_clean = df_clean.reset_index()
        
        self.df = df_clean
        
    def drop_non_legal_cards(self):
        
        df_clean = self.df.copy()
        
        legal_columns = [current_col for current_col in df_clean.columns if bool(re.search(pattern = r"_legal$",
                                                                                           string = current_col))]
        
        temp = df_clean[legal_columns]
        temp = temp.fillna(False).astype(int)
        
        df_clean["legal_sum"] = temp.sum(axis = 1)
        
        self.df = df_clean[df_clean["legal_sum"] != 0]
        
    def drop_unnecessary_columns(self):
        
        df_clean = self.df.copy()
        df_clean = df_clean.drop(self.drop_columns, axis = 1)
        df_clean.columns = [current_col.lower() for current_col in df_clean.columns]
        self.df = df_clean
        
    def make_data_unique(self):
        
        df_clean = self.df.copy()
        
        df_clean = df_clean.groupby("card_name").head(1).reset_index(drop = True)
        
        self.df = df_clean
        

    def process_data(self):
        
        if self.df is None:
            
            raise ValueError("No data loaded. Call load_data() first.")
        
        self.filter_tokens_and_basic_lands()
        self.split_types()
        self.pivot_longer_double_cards()
        self.is_color()
        self.is_in_format()
        self.is_card_type()
        self.get_rarity()
        self.create_keyword_string()
        self.create_legalities()
        self.count_number_of_color_pips()
        self.create_subtype()
        self.drop_non_legal_cards()
        self.clean_power_and_toughness()
        self.planeswalker_loyalty()
        self.drop_unnecessary_columns()
        self.make_data_unique()
        
class CardRecommenderModel:
    
    def __init__(self, data_processor):
        
        self.data_processor = data_processor
        self.stopwords = set(stopwords.words("english"))
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
                                            min_count = 1, 
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
            
    def tsne_data_visualization(self, n_components = 2):
        
        self.tsne_model = TSNE(n_components = n_components, random_state = 99)
        self.tsne_features = self.tsne_model.fit_transform(self.unscaled_model_features_pca)
        
        plt.figure(figsize = (12, 8))

        for cluster in np.unique(self.cluster_names):

            cluster_mask = self.cluster_names == cluster
            
            self.tsne_scatter = plt.scatter(self.tsne_features[cluster_mask, 0], self.tsne_features[cluster_mask, 1],
                                            label = f"Cluster {cluster}")
        
        plt.title("MTG Cards Clusters by K-Means")
        plt.xlabel("t-SNE Component 1")
        plt.ylabel("t-SNE Component 2")
        plt.legend()
        
        # add a few card names to the plot
        sample_card_data = self.data_processor.df.sample(25, replace = False)
        sample_card_indices = sample_card_data.index.tolist()
        
        for index in sample_card_indices:
            
            plt.annotate(self.data_processor.df.loc[index, "card_name"],
                         (self.tsne_features[index, 0], self.tsne_features[index, 1]))
            
        plt.tight_layout()
        plt.show()
        
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

    def random_forest_feature_importance_visualization(self):

        self.rf_cluster_model_feature_importance = self.rf_cluster_model.feature_importances_

        indices = np.argsort(self.rf_cluster_model_feature_importance)[::-1][:20]
        plt.figure(figsize = (12, 6))
        self.feature_importance_bar_graph = plt.barh(range(20), self.rf_cluster_model_feature_importance[indices])
        plt.yticks(range(20), [self.feature_names[i] for i in indices])
        plt.xlabel("Feature Importance")
        plt.title("Feature Importance for Card Recommender Model")
        plt.tight_layout()
        plt.show()

    def plot_card_type_clusters(self):

        cluster = 0

        fig, axs = plt.subplots(2, 4, figsize = (15, 15))
        fig.suptitle("Most Common Card Type by Cluster")

        for i in range(2):
            for j in range(4):

                cluster_mask = self.card_type_by_cluster["cluster"] == cluster
                cluster_values = self.card_type_by_cluster.loc[cluster_mask]
            
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

                cluster_mask = self.card_subtype_by_cluster["cluster"] == cluster
                cluster_values = self.card_subtype_by_cluster.loc[cluster_mask]
            
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

                cluster_mask = self.color_by_cluster["cluster"] == cluster
                cluster_values = self.color_by_cluster.loc[cluster_mask]

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

    def train_models(self):

        self.legal_cards_for_format()
        self.tokenize_text()
        self.trainWord2Vec_model()
        self.average_word_vector_to_df()
        self.get_model_inputs()
        self.train_KNN_model()
        self.train_kmeans_model()
        self.RandomForest_for_clusters()
        
        
        
        
        
        
        
        
        
            
            
        
        
        
        
        
 
        
 
        
        
        
        
   
    
        
    
        
        
        
        
        
        
        
        
        
        
        
        
        
    
        
        
        
        
        
        
        
        
        
        
        
                    
    
                
        
 