# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 23:14:41 2025

@author: holli
"""
def get_url_data(url):

  request_response = requests.get(url)

  if request_response.status_code == 200:
    return request_response.json()

  else:
    return request_response.status_code

def json_to_dataframe(json_data):

  if isinstance(json_data, list):
    return pd.DataFrame(json_data)

  elif isinstance(json_data, dict):
    return pd.DataFrame([json_data])

  else:
    return pd.DataFrame([json_data])

def get_requested_data(url):

  return json_to_dataframe((get_url_data(url)))

def filter_tokens_and_basic_lands(df):
    
    df_reduced = df[SELECTED_COLUMNS]

    # Filter for English only cards and non tokens and filter out basic lands
    df_reduced_clean = df_reduced.loc[(df_reduced.layout.isin(["normal", "adventure", "transform", "split",
                                                               "modal_dfc", "planar", "reversilbe_card", "meld",
                                                               "saga", "class", "case", "flip",
                                                               "leveler", "prototype"])) &
                                      ~(df_reduced.name.isin(["Forest", "Plains", "Swamp", "Island",
                                                              "Mountain"]))]
    return df_reduced_clean

def get_card_subtypes(df):
    
    df_clean = df.copy()
    
    # First, ensure split_columns has the correct number of columns
    split_columns = df["type_line"].str.split("—", expand=True)
    
    # Check the number of columns in split_columns
    split_columns.columns = ["card_type", "card_subtype1", "card_subtype2", "card_subtype3"]
    
    
    # Now assign the split columns to all_mjr_cards_data_clean only where is_land == 0
    # Ensure the indexes align
    for card_column in split_columns.columns:
        df_clean[card_column] = split_columns[card_column].str.strip() # trim whitespace
        
    return df_clean

def is_color(df):
    
    df_reduced = df.copy()
    df_clean = df.copy()
    
    for color, color_char in COLORS_DICT.items():
        
        if color in ["blue", "red", "white", "black", "green"]:

            df_clean.loc[:, f"is_{color}"] = df_reduced["color_identity"].apply(
                lambda x: True if color_char in x else False)

            df_clean[f"produce_{color}"] = np.select(
                condlist=[
                    df_clean["produced_mana"].apply(
                        lambda x: color_char in x if isinstance(x, list) else False),
                    df_clean["produced_mana"].isna()
                ],
                choicelist = [True, np.nan],
                default = False
                ).astype(bool)
        else:
            
            df_clean.loc[:, f"is_{color}"] = df_reduced["color_identity"].apply(lambda x: True if len(x) == 0 else False)


            df_clean[f"produce_{color}"] = np.select(
                condlist=[df_clean["produced_mana"].apply( 
                    lambda x: "C" in x if isinstance(x, list) else False),
                    df_clean["produced_mana"].isna()],
                choicelist=[True, np.nan],
                default = False
                ).astype(bool)
            
    return df_clean

def is_in_format(df):
    
    df_clean = df.copy()
    
    df_clean = pd.concat([df_clean,
                          (df_clean["legalities"].apply(pd.Series))],
                           axis = 1,
                           ignore_index = False).reset_index(drop = True)
    
    all_games = set([game for sublist in df_clean["games"] for game in sublist])
    
    for current_game in all_games:

        df_clean[f"is_in_{current_game}"] = np.select(
        
            condlist = [df_clean["games"].apply(
                lambda x: current_game in x if isinstance(x, list) else False
                ), 
                df_clean["games"].isna()
                ], 
            choicelist = [True, np.nan], 
            default = False).astype(bool)
        
    return df_clean

def create_keyword_string(df):
    
    df["keywords_string"] = df["keywords"].apply( 
        lambda x: ", ".join(x) if isinstance(x, list) and len(x) > 0 else np.nan)
    
    return(df)


def create_legalities(df):  
    
    df_clean = df.copy()
    
    for game in GAME_FORMATS:
    
        df_clean[game] = np.select(

        condlist = [ 
            df_clean[game] == "legal",
            df_clean[game] == "not_legal",
            df_clean[game] == "banned",
            df_clean[game].isna()
        ],

        choicelist = [True, False, False, np.nan]
        
        ).astype(bool)
    
    return df_clean

def write_data_local(df, raw_data, file_name):
    
    if raw_data == True:
        
        file_path = ("C:\\Users\\holli\\Documents\\MTG Scryfall App\\Data\\Raw Data File" + "\\" +
                     file_name + ".csv")
        
    else:
        
        file_path = ("C:\\Users\\holli\\Documents\\MTG Scryfall App\\Data\\Processed Data File" + "\\" +
                     file_name + ".csv")
        
    df.to_csv(file_path, sep = ",", encoding = "utf-8", index = False, header = True)
    
def count_number_of_color_pips(df):
    
    color_pips_dict = {"blue": "U",
                       "red": "R",
                       "white": "W",
                       "black": "B",
                       "green": "G",
                       "colorless": "C"}
    
    df_output = df.copy()
    
    df_output["mana_cost"] = df_output["mana_cost"].apply(lambda x: re.sub(pattern = r"[{}]",  repl = "", string = str(x)))
    
    for color, color_char in color_pips_dict.items():
        
        df_output[f"{color}_pips"] = df["mana_cost"].apply(lambda x: len(re.findall(re.escape(color_char), str(x)))
                                                           )
        
    df_output["generic_pips"] = df_output["mana_cost"].apply(lambda x: sum(int(d) for d in re.findall(r"\d+", str(x))))
    
    df_output["generic_pips"] = np.select(
        
        condlist = [df_output["mana_cost"].apply(lambda x: bool(re.search(r"X", str(x)))
                                          ),
                    df_output["mana_cost"].isna()
                    ],
        choicelist = [np.inf, np.nan],
        default = df_output["generic_pips"]
        
        )
    
    return df_output

def double_cards(df):
    
    df_clean = df.copy()
    
    df_clean["double_cards"] = np.select(
        
        condlist = [df_clean["name"].apply(lambda x: bool(re.search(r"\//", str(x)))),
                    df_clean["name"].isna()],
        choicelist = [True, np.nan],
        default = False
        
    ).astype(bool)
    
    df_clean_double_cards = df_clean.loc[df_clean["double_cards"] == True, ]
    
    
    return df_clean

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
    
    
    







