# Getting all player data from KBO and NPB teams who have played in the MLB
# The first step involves getting the links to every team's lineup for every season

import bs4
import numpy as np 
import pandas as pd 
from requests_html import AsyncHTMLSession
import time
from selenium import webdriver

league_codes = [
    ('KBO', 'KBO'),
    ('NPB_central', 'JPCL'),
    ('NPB_pacific', 'JPPL')
]
league_url = 'https://www.baseball-reference.com/register/league.cgi?code={league}&class=Fgn'

# Open session and generate blank list
session = AsyncHTMLSession()
link_list = []

# Loop for each league and gather all team links
for league_tup in league_codes:
    print('Beginning', league_tup[0], 'scrape...')
    
    # Render the page's JS
    res = await session.get(league_url.format(league=league_tup[1]))
    await res.html.arender()
    print(league_tup[0], 'rendered.')
    
    # Make some soup and take a look at the lg_history table
    league_history_soup = bs4.BeautifulSoup(res.html.html, 'lxml')
    league_history_rows = league_history_soup.select('#lg_history tbody tr')

    count = 0
    i = 0
    
    # Loop over each row and take each individual team's links
    while count < 20:  # take the last 20 seasons of players
        if league_history_rows[i].get('class') == 'thead':
            # This is a catch for blank rows, so as not to have a blank season
            i += 1
        else:
            for link in league_history_rows[i].select('td a'):
                # append the league it belongs to, and the link's reference
                link_list.append((league_tup[0], link.get('href')))
            i += 1
            count += 1
    
    print(len(link_list), 'total links after completion of', league_tup[0])
    print()
    time.sleep(5)
    
print('Completed.')

# Obtaining only the MLB players' ids
# The second step involves chasing each of these team links, and identifying the player_ids that are designated as former MLB players
# One thing to keep in mind, is that these identify HOF'ers as well, so each players data has to be checked to make sure that they were in fact an MLB player
# Another thing, Selenium was used as request_html continued to fail when rendering the page due to timeouts

# Open browser and generate blank list
browser = webdriver.Firefox()
id_list = []
curr_league = ''

# Loop for each of the team links from the previous section
for i, link_tup in enumerate(link_list):
    print('Next iteration begins')
    
    # wait before calling
    time.sleep(float(np.random.rand(1)) * 5 + 2.5)  # random call times b/w 2.5 and 7.5 seconds 
    
    # Update progress of scraping
    if link_tup[0] != curr_league:
        curr_league = link_tup[0]
        print('Scraping', curr_league, '...')
    curr_id_length = len(id_list)
    
    # Connect into Baseball-Reference
    print('Opening page...')
    browser.get('https://www.baseball-reference.com' + link_tup[1])
    print('Obtained session, sleeping before parsing HTML')
    time.sleep(1)
    print('Page', i + 1, 'rendered.')
    
    # Cut to MLB pitchers and batters
    mlb_batters = browser.find_elements_by_css_selector('#team_batting tbody tr td strong a')
    mlb_pitchers = browser.find_elements_by_css_selector('#team_pitching tbody tr td strong a')
    
    # Loop over each of these and add to the id_list (only if not in the list already) 
    for bttr in mlb_batters:
        bttr_id = bttr.get_attribute('href').split('id=')[1]
        if bttr_id not in id_list:
            id_list.append(bttr_id)
    for ptchr in mlb_pitchers:
        ptchr_id = ptchr.get_attribute('href').split('id=')[1]
        if ptchr_id not in id_list:
            id_list.append(ptchr_id)

    print('Page', i + 1, 'scraped.', len(id_list) - curr_id_length, 'new players added.')
    print(len(id_list), 'total players.')
    print()

print('Completed.')
browser.quit()

player_ids = pd.DataFrame(id_list, columns=['player_id'])

player_ids.to_csv('./player_ids_all.csv', index=False)