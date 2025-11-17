# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 23:14:41 2025

@author: holli
"""
class MTGDataProcessor:
    
    def __init__(self, selected_columns, colors_dict, card_types, card_subtypes,
                 game_formats, non_legal_sets, basic_lands, card_layout_keep,
                 color_pips_dict, rarity, drop_columns):
        
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
        
        self.df = df_output
        
    def planeswalker_loyalty(self):
        
        df_clean = self.df.copy()
        
        df_clean["planeswalker_loyalty"] = df_clean["loyalty"].apply(
            
            lambda x: np.inf if bool(re.search(pattern = r"X", string = str(x))) else None
            
            ) 
        
        df_clean["planeswalker_loyalty"] = df_clean["loyalty"].apply(
            
            lambda x: int(re.search(r"(\d+)", str(x)).group(1)) if re.search(r"(\d+)", str(x)) else None
            
            )
        
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
        
        df_clean = df_clean.groupby(["id", "card_name"]).head(1).reset_index()
        
        self.df = df_clean
        

    def process_data(self):
        
        """Run the full processing pipeline"""
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
        self.planeswalker_loyalty()
        self.count_number_of_color_pips()
        self.create_subtype()
        self.drop_non_legal_cards()
        self.drop_unnecessary_columns()
        self.make_data_unique()
        print("Dataframe returned")
        
    # Add all your other methods as instance methods...
    
    def save_data(self, file_name, raw_data = False):
        
        if self.df is None:
            
            raise ValueError("No data to save.")
            
            
        if raw_data == True:
            
            file_path = ("C:\\Users\\holli\\Documents\\MTG Scryfall App\\Data\\Raw Data File" + "\\" +
                         file_name + ".csv")
        
        else:
            
            file_path = ("C:\\Users\\holli\\Documents\\MTG Scryfall App\\Data\\Processed Data File" + "\\" +
                         file_name + ".csv")
            
        self.df.to_csv(file_path, sep = ",", encoding = "utf-8", index = False, header = True)
        
class CardRecommendorModel:
    
    def __init__(self, data_processor):
        
        self.data_processor = data_processor
        self.stopwords = set(stopwords.words("english"))
        nltk.download("punkt")
        self.orcale_text_model = None 
        self.keyword_text_model = None 
        self.valid_game_format = None
        self.initalize_game_format()
            
    def initalize_game_format(self):
        
        print("Welcome to the Magic the Gathering card recommender!\n\n")
        print("Which format will you be playing. Your choices are:")
        
        for game_format in self.data_processor.game_formats:
            
            print(game_format)
            
        self.get_game_format()
        
    def get_game_format(self):
        
        while True:
            
            if user_input in self.data_processor.game_formats:
                
                user_input = input().strip().lower()
                self.valid_game_format = user_input
                print(f"Game format set to: {self.valid_game_format}")
                break          
            
            else: 
                
                print("Please choose valid game format")
                
                for game_format in self.data_processor.game_formats:
                    print(game_format)
    
    def legal_cards_for_format(self):
        
        self.data_processor.df = self.data_processor.df[self.data_processor.df[f"{self.valid_game_format}_Legal"] == True]
    
    def tokenize_text(self):
        
        self.data_processor.df["orcale_text_tokens"] = self.data_processor.df["orcale_text"].apply(self.tokenize_words)
        self.data_processor.df["keyword_string_tokens"] = self.data_processor.df["keyword_string"].apply(self.tokenize_words)
        
    def tokenize_words(self, text):
        
        if not text or pd.isna(text):
            
            return []
        
        else: 
            
            token = word_tokenize(text.lower()) 
            filtered_token = [word for word in token if word not in self.stopwords] 
            return filtered_token
        
    def trainWord2Vec_model(self):

        self.orcale_text_model = Word2Vec(sentences = self.data_processor.df["orcale_text_tokens"],
                                          vector_size=100,
                                          window=5, 
                                          min_count=1, 
                                          workers=4)
        
        self.keyword_text_model = Word2Vec(sentences = self.data_processor.df["keyword_string_tokens"],
                                           vector_size=100,
                                           window=5, 
                                           min_count=1, 
                                           workers=4)
        
        
        
        
        
        
        
        
        
        
        
                    
    
                
        
 