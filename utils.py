# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 23:14:41 2025

@author: holli
"""
class MTGDataProcessor:
    
    def __init__(self, selected_columns, colors_dict, card_types, 
                 game_formats, non_legal_sets, basic_lands, card_layout_keep,
                 color_pips_dict):
        
        self.selected_columns = selected_columns
        self.colors_dict = colors_dict
        self.card_types = card_types
        self.game_formats = game_formats
        self.non_legal_sets = non_legal_sets
        self.basic_lands = basic_lands
        self.card_layout_keep = card_layout_keep
        self.color_pips_dict = color_pips_dict
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
        
        df_reduced = self.df[self.selected_columns]

        # Filter for English only cards and non tokens and filter out basic lands
        df_reduced_clean = df_reduced.loc[(df_reduced.layout.isin(self.card_layout_keep)) &
                                          ~(df_reduced.name.isin(self.basic_lands)) &
                                          ~(df_reduced.set_name.isin(self.non_legal_sets))]
        self.df = df_reduced_clean
        
    def is_color(self):
    
        df_clean = self.df.copy()
        
        for color, color_char in COLORS_DICT.items():
        
            if color in ["blue", "red", "white", "black", "green"]:

            # Check if color is in color identity
                df_clean.loc[:, f"is_{color}"] = df_clean["color_identity"].apply(
                    lambda x: color_char in x if isinstance(x, list) else False
                ).astype("boolean") 
            
            # Handle NaN values for color identity
                df_clean.loc[df_clean["color_identity"].isna(), f"is_{color}"] = pd.NA
            
            # Check if color mana is produced
                df_clean[f"produced_{color}"] = df_clean["produced_mana"].apply(
                lambda x: color_char in x if isinstance(x, list) else False
                ).astype("boolean")
            
            # Handle NaN values for produced mana
                df_clean.loc[df_clean["produced_mana"].isna(), f"produced_{color}"] = pd.NA
            
            else:  # This is for colorless
            # Colorless cards have empty color identity
                df_clean.loc[:, f"is_{color}"] = df_clean["color_identity"].apply(
                    lambda x: len(x) == 0 if isinstance(x, list) else False
                    ).astype("boolean")
            
                # Handle NaN values for color identity
                df_clean.loc[df_clean["color_identity"].isna(), f"is_{color}"] = pd.NA
            
                # Check if colorless mana is produced
                df_clean[f"produced_{color}"] = df_clean["produced_mana"].apply(
                    lambda x: "C" in x if isinstance(x, list) else False
                    ).astype("boolean")
            
            # Handle NaN values for produced mana
                df_clean.loc[df_clean["produced_mana"].isna(), f"produced_{color}"] = pd.NA
            
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
            
            df_clean.loc[df_clean["games"].isna(), f"is_in_{current_game}"] = pd.NA
            
        self.df = df_clean
        
    def is_card_type(self):
        
        df_clean = self.df.copy()
        
        for card_type in self.card_types:
            
            has_card_type = df_clean["type_line"].str.contains(
                
                card_type, na = False, regex = True
                
            )
            
            df_clean[f"is_{card_type}"] = False
            df_clean.loc[has_card_type, f"is_{card_type}"] = True
            df_clean.loc[df_clean["type_line"].isna(), f"is_{card_type}"] = pd.NA
            
            df_clean[f"is_{card_type}"] = df_clean[f"is_{card_type}"].astype("boolean")
            
            search_string = f"{card_type} —"
            
            df_clean["type_line"] = df_clean["type_line"].apply(
                
                lambda x: re.sub(pattern = search_string, repl = "", string = x)
                
            )

        self.df = df_clean
        
    def create_keyword_string(self):
        
        df_clean = self.df.copy()
        
        df_clean["keywords_string"] = df_clean["keywords"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) and len(x) > 0 else pd.NA)
        
        self.df = df_clean
        
    def create_legalities(self):  
        
        df_clean = self.df.copy()
        
        for game in self.game_formats:
            
            game_string = "_".join([game, "legal"])
            
            df_clean[game_string] = False
            
            df_clean.loc[df_clean[game] == "legal", game_string] = True
            df_clean.loc[df_clean[game] == "not_legal", game_string] = True
            df_clean.loc[df_clean[game] == "banned", game_string] = True
            
            df_clean.loc[df_clean[game].isna(), game_string] = pd.NA
        
        self.df = df_clean
        
    def count_number_of_color_pips(self):
        
        df_output = self.df.copy()
        
        df_output["mana_cost"] = df_output["mana_cost"].apply(lambda x: re.sub(pattern = r"[{}]",  repl = "", string = str(x)))
        
        for color, color_char in self.color_pips_dict.items():
            
            df_output[f"{color}_pips"] = df_output["mana_cost"].apply(lambda x: len(re.findall(re.escape(color_char), str(x))))
            
        df_output["generic_pips"] = df_output["mana_cost"].apply(lambda x: sum(int(d) for d in re.findall(r"\d+", str(x))))
        
        df_output["generic_pips"] = np.select(
            
            condlist = [df_output["mana_cost"].apply(lambda x: bool(re.search(r"X", str(x)))                                   ),
                        df_output["mana_cost"].isna()],
            choicelist = [np.inf, pd.NA],
            default = df_output["generic_pips"]
            
        )
        
        self.df = df_output

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
#        self.is_card_type()
        self.create_keyword_string()
        self.create_legalities()
        self.count_number_of_color_pips()
        
        return self.df
    
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

def create_database(NEW_DB_NAME, server):
    
    conn = psycopg2.connect(
        
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=get_db_password(server),
            dbname="postgres"  # connect to default maintenance DB
        )
    
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # enable autocommit for DB creation
        
        # Create a cursor to execute SQL commands
    cursor = conn.cursor()
        
    # Prevent SQL injection by using sql.Identifier
    create_db_query = sql.SQL("CREATE DATABASE {}").format( 
        sql.Identifier(NEW_DB_NAME)
        )
        
    # Execute the database creation command
    cursor.execute(create_db_query)
    print(f"Database '{NEW_DB_NAME}' created successfully!")
        
    except psycopg2.Error as e:
        
        print(f"Error creating database: {e}")
    
    finally:
        
        # Close cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
def get_db_password(server):
    
    server_password = DB_PASSWORDS.loc[DB_PASSWORDS["database"] == server, "password"][0]
    
    return server_password

def create_cards_table(NEW_DB_NAME):
    
    
    







