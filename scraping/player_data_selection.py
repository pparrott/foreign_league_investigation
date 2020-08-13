#!/usr/bin/env
import bs4
import numpy as np 
import pandas as pd 
from requests_html import AsyncHTMLSession
from selenium import webdriver
import time 

# Player ids
df_ids = pd.read_csv('./player_ids_all.csv')
list_ids = df_ids.player_id.tolist()

# Parameters for table cleaning
bat_change_dict = {'Year': int,
                   'Age': int,
                   'G': int,
                   'PA': int,
                   'AB': int,
                   'R': int,
                   'H': int,
                   '2B': int,
                   '3B': int,
                   'HR': int,
                   'RBI': int,
                   'SB': int,
                   'CS': int,
                   'BB': int,
                   'SO': int,
                   'BA': float,
                   'OBP': float,
                   'SLG': float,
                   'OPS': float,
                   'TB': int,
                   'GDP': int,
                   'HBP': int,
                   'SH': int,
                   'SF': int,
                   'IBB': int}

pitch_change_dict = {'Year': int,
                     'Age': int,
                     'W': int,
                     'L': int,
                     'W-L%': float,
                     'ERA': float,
                     'RA9': float,
                     'G': int,
                     'GS': int,
                     'GF': int,
                     'CG': int,
                     'SHO': int,
                     'SV': int,
                     'IP': float,
                     'H': int,
                     'R': int,
                     'ER': int,
                     'HR': int,
                     'BB': int,
                     'IBB': int,
                     'SO': int,
                     'HBP': int,
                     'BK': int,
                     'WP': int,
                     'BF': int,
                     'WHIP': float,
                     'H9': float,
                     'HR9': float,
                     'BB9': float,
                     'SO9': float,
                     'SO/W': float}

# set up browser for selenium
browser = webdriver.Firefox()
player_url = 'https://www.baseball-reference.com/register/player.fcgi?id={player_id}'
df_player_list = []
df_pitcher_list = []

for i, player_id in enumerate(list_ids):
    # wait before calling
    print('Wait before next call')
    time.sleep(float(np.random.rand(1)) * 5 + 2.5)

    # Connect into Baseball-Reference
    print('Opening page...')
    browser.get(player_url.format(player_id=player_id))
    print('Obtained session, sleeping before parsing HTML')
    time.sleep(3)
    print('Page', i + 1, 'of', len(list_ids), 'rendered.')

    # Grab player name and position
    player_name = browser.find_element_by_css_selector('div h1[itemprop = "name"] span').text
    player_position = browser.find_element_by_css_selector('div[itemtype="https://schema.org/Person"] p').text.split(': ')[1] 

    # Check if the player is a pitcher, then allocate appropriate 
    if 'pitcher' in player_position.split(',')[0].lower():  # assumption is first position must be pitcher
        table_to_find = '#div_standard_pitching'
        table_dict = pitch_change_dict
        pitcher = True
    else:
        table_to_find = '#div_standard_batting'
        table_dict = bat_change_dict
        pitcher = False

    print(player_id, 'is', player_name, ', and is a', player_position)
    print('Is a pitcher?', pitcher)
    print('...')

    # Grab the table
    player_table = browser.find_elements_by_css_selector(table_to_find)
    player_table_soup = bs4.BeautifulSoup(player_table[0].get_attribute('innerHTML'))
    df_loop = pd.read_html(str(player_table_soup))[0]
    print('Table acquired,', len(df_loop), 'rows.')

    # Clean the table a bit
    # Cut out aggregate data
    agg_location = df_loop.index[df_loop['Year'] == 'Year'].tolist()[0]
    df_loop = df_loop.iloc[:agg_location]
    # Remove NA's
    df_loop = df_loop[~df_loop.isna().all(axis=1)]
    # Make sure that Year is 4 characters max
    df_loop['Year'] = df_loop['Year'].str[:4]
    # Change the table's data types
    for j in table_dict:
        df_loop[j] = df_loop[j].astype(table_dict[j], errors='ignore')

    # Add identifiers to the table
    df_loop = df_loop.assign(id=player_id, name=player_name, position=player_position)

    # append to list, and continue
    if pitcher:
        df_pitcher_list.append(df_loop)
        print('Table appended to pitchers.', len(df_pitcher_list), 'pitchers total.')
    else: 
        df_player_list.append(df_loop)
        print('Table appended to fielders.', len(df_player_list), 'fielders total.')
    print()

print('Completed.')
browser.quit()

df_pitcher = pd.concat(df_pitcher_list)
df_fielder = pd.concat(df_player_list)

df_pitcher.to_csv('./pitcher_historial_data.csv', index=False)
df_fielder.to_csv('./fielder_historical_data.csv', index=False)