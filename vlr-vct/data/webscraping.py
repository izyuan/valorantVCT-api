import requests
from bs4 import BeautifulSoup
from lxml import html
import json
import re
import sys

#maybe cache it? 
import sqlite3

vlrregionDict = {
    'na': ['north-america', 'North-America'],
    'eu': ['europe', 'Europe'],
    'ap': ['asia-pacific', 'Asia-Pacific'],
    'la': ['latin-america', 'Latin-America'],
    'la-s': ['la-s', 'La-S'],
    'la-n': ['la-n', 'La-N'],
    'oce': ['oceania', 'Oceania'],
    'kr': ['korea', 'Korea'],
    'mn': ['mena', 'Mena'],
    'gc': ['game-changers', 'Game-Changers'],
    'br': ['brazil', 'Brazil'],
    'cn': ['china', 'China']
}
vlrmapDict = {
    "1": ["bind", "Bind"],
    "2": ["Haven", "haven"],
    "3": ["Split", "split"],
    "5": ["ascent", "Ascent"],
    "6": ["Icebox", "icebox"],
    "8": ["Breeze", "breeze"],
    "9": ["Fracture", "fracture"],
    "10": ["pearl", "Pearl"],
    "11": ["Lotus", "lotus"],
    "12": ["sunset", "Sunset"]
}
vlrtimestampDict = {
    "30d" : [30, "30"],
    "60d" : [60, "60"],
    "90d": [90, "90"],
    "all": "all"
}
vlreventDict = {
    "1921": ["masters madrid", "Masters Madrid"], 
    "1923" : ["americas kickoff", "Americas Kickoff"], 
    "1657" : ["champions 2023", "Champions 2023"]
}

spkregionDict = {
    "5" : ["Brazil", "brazil"], 
    "2": ["europe", "Europe"], 
    "4" : ["Japan", "japan"],
    "3" : ["Korea", "korea"], 
    "6" : ['la-n', 'La-N'],
    "10": ['la-s', 'La-S'],
    "1": ['north-america', 'North-America'],
    "8": ['oceania', 'Oceania'], 
    "9" : ["other"],
    "7": ["Southeast-Asia", "southeast-asia"]
}
spkmapDict = {
    "2": ["bind", "Bind"],
    "3": ["Haven", "haven"],
    "1": ["Split", "split"],
    "4": ["ascent", "Ascent"],
    "5": ["Icebox", "icebox"],
    "6": ["Breeze", "breeze"],
    "7": ["Fracture", "fracture"],
    "8": ["pearl", "Pearl"],
    "9": ["Lotus", "lotus"],
    "10": ["sunset", "Sunset"]
}
spkeventDict = {
    "3040": ["masters madrid", "Masters Madrid"], 
    "2998" : ["americas kickoff", "Americas Kickoff"], 
    "2543" : ["champions 2023", "Champions 2023"],
    "1189": ["Champions Tour 2023 Americas League", "champions tour 2023 americas league"]
}


def getKey(d, value): #helper function
    """
    Return the key in the dictionary d that corresponds to the value.
    Value comparison accounts for both lists and single-value entries. 
    Case-insensitive comparison for string values.
    """
    for key, val in d.items():
        if isinstance(val, list):
            if any(str(v).lower() == str(value).lower() for v in val):
                return key
        else:
            if isinstance(val, str) and isinstance(value, str):
                if val.lower() == value.lower():
                    return key
            elif val == value:
                return key
    return None

def match_td_style(tag):
    return (tag.name == "td" and
            tag.get("style") == "white-space: nowrap; padding-top: 0; padding-bottom: 0;")

def scrapePlayerStats (regionID: str="all", eventSeries: str="61", eventID: int="all", minRounds: int="all", minRating: int="all", agent:str="all", mapID: str="all", timespan:int=60): #61 for franchising valorant,
    """get the stats of players

    Args:
        each param is a filter essentially 
    """
    #getting the id for vlr
    region = getKey(vlrregionDict, regionID) or regionID
    map = getKey(vlrmapDict, mapID) or mapID 
    Timespan = getKey(vlrtimestampDict, timespan) or timespan
    eventID = getKey(vlreventDict, eventID) or "all"
    
    url = f"https://www.vlr.gg/stats/?event_group_id={eventSeries}&event_id={eventID}&series_id=all&region={region}&country=all&min_rounds={minRounds}&min_rating={minRating}&agent={agent}&map_id={map}&timespan={Timespan}"
    print(url)
    
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'lxml')
    
    players_stats = [] 
    for row in soup.select("tbody tr"): 
        player_info = row.get_text(separator=" ").strip()
        player_info_list = player_info.split()
        player_name = player_info_list[0] #player name
        organization = player_info_list[1] if len(player_info_list) > 1 else "None" #player org
        
        rounds_played = row.select_one("td.mod-rnd").get_text(strip=True) if row.select_one('td.mod-rnd') else None
        # Extracting the stats from the "mod-color-sq" class
        stats = [stat.get_text() for stat in row.select("td.mod-color-sq")] 
        if len(stats) == 11: 
            rating, average_combat_score, kill_death_ratio, kast, average_damage_per_round, kills_per_round, assists_per_round, first_kills_per_round, first_deaths_per_round, headshot_percentage, clutch_success_percentage = stats
            if clutch_success_percentage == None:
                clutch_success_percentage = "none attempted"
        else:
            continue 
        clutch_fraction = row.select_one('td.mod-cl').get_text(strip=True) if row.select_one('td.mod-cl') else None
        kill_max_tag = row.select_one('td.mod-a.mod-kmax')
        kill_max_value = kill_max_tag['data-sort-value'] if kill_max_tag and kill_max_tag.has_attr('data-sort-value') else None
        following_stats = kill_max_tag.find_next_siblings('td')[:5] if kill_max_tag else []
        if following_stats and len(following_stats) == 5:
            total_kills, total_deaths, total_assists, total_first_kills, total_first_deaths = [stat.get_text(strip=True) for stat in following_stats]
        else:
            continue  # Skip if there are not enough following stats

            #extracting 
        try: 
            players_stats.append({
                "player": player_name,
                "organization": organization, 
                "rounds" : rounds_played,
                "acs": average_combat_score,
                "kdr": kill_death_ratio, 
                "kast": kast,
                "adr": average_damage_per_round,
                "kpr": kills_per_round,
                "apr": assists_per_round,
                "fkpr": first_kills_per_round,
                "fdpr": first_deaths_per_round,
                "hs%": headshot_percentage,
                "cl%": clutch_success_percentage,
                "cl": clutch_fraction,
                "kmax" : kill_max_value,
                "k" : total_kills,
                "d": total_deaths,
                "a": total_assists, 
                "fk" : total_first_kills, 
                "fd" : total_first_deaths
            })
        except:
            return {"status": "failed"}

    data = {"players_stats": players_stats}
    
    jsondata = json.dumps(data, indent=4)

    return jsondata
  
  
def scrapeAndMapAgentStats (event: str=None): 
    url = f"https://www.vlr.gg/event/agents/{event}/"
    print(f" url : {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    agentpickrates = []
    map_stats = []
    row_stats = []
    map_rows = []
    map_names = []
    
    img_tags = soup.find_all('img', {'src': re.compile(r'/agents/')})
    agents = [re.search(r'/agents/(\w+)\.png', img_tag['src']).group(1) for img_tag in img_tags]
    #agents good
    
    for tr in soup.find_all('tr'):
        #extracting agent PR
        tds = tr.find_all('td', class_="mod-color-sq")
        map_tds = tr.find_all("td", class_="mod-right")
        #extracting agent PRS
        if tds:
            row_stats = []
            for td in tds:
                color_sq = td.find_all('div', class_='color-sq') #looking for the div 
                if color_sq:
                    span = color_sq[0].find('span') #find span and get text
                    if span:
                        value = span.get_text().strip()
                        row_stats.append(value)
            agentpickrates.append(row_stats)
            
        #extracting map stats
        if map_tds:
            map_rows = []
            for v in map_tds: #taking out each value 
                map_value = v.get_text().strip()
                map_rows.append(map_value)
            map_stats.append(map_rows)
        
        #using the function to get style, and then finding the map names by td style because there is no class
        matching_tds = tr.find_all(match_td_style)
        for maptd in matching_tds:
            map_names.append(maptd.text.strip())
            map_names = [item.split()[-1] for item in map_names if item.strip()]

    #dictionary!
    data = {
        "global": {
            "agent_pick_rates": {agent: rate for agent, rate in zip(agents, agentpickrates[0])},
            "map_stats": {
                "maps_picked": map_stats[0][0],
                "atk_win_rate": map_stats[0][1],
                "def_win_rate": map_stats[0][2]
            }
        },
        "maps": {}
    }
    #adding for loop for maps
    for i, map_name in enumerate(map_names[1:], start=1):  # Skip 'Global'
        data["maps"][map_name] = {
            "agent_pick_rates": {agent: rate for agent, rate in zip(agents, agentpickrates[i])},
            "map_stats": {
                "maps_picked": map_stats[i][0],
                "atk_win_rate": map_stats[i][1],
                "def_win_rate": map_stats[i][2]
            }
        }
    
    jsondata = json.dumps(data, indent=4)
    
    return jsondata
        

def scrapeTeamStats (team:str="all",event: str="all", core:str="all", date_start: str="", date_end:str=""): #dates must be in YYYY-MM-DD 
    
    #getting the html for the stats
    url = f"https://vlr.gg/team/stats/{team}/?event_id={event}&series_id=all&core_id{core}&date_start={date_start}&date_end={date_end}"
    print(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    
    try:
        #finding the table for the statistics
        table = soup.find("table", class_="wf-table mod-team-maps")
        rows = table.find_all("tr")
    except Exception as e: 
        print(f"error finding data: check the parameters \n Error Message : {e}")
        #exit the program if excpetion is hit
        sys.exit(1)
    
    data_list = []
    single_map_data = []
    
    for row in rows: 
        cells = row.find_all("div", class_="mod-first")
        for cell in cells: 
            text = cell.get_text().strip()
            single_map_data.append(text)
            #getting only the necessary data
            if len(single_map_data) == 12:
                break 
        
        #if single map data is none, continue to the next iteration ( we dont need this)
        if len(single_map_data) == 0:
            continue
        
        #extracting number played 
        map_name_times_played = single_map_data[0]
        match = re.search(r'\((\d+)\)', map_name_times_played)
        number_num = match.group(1)
        perm_map_list = map_name_times_played.split(" ")
        map_name = perm_map_list[0]
        #creating a dictionary
        single_map_dict = {
        "map_name" : map_name, 
        "times_played": number_num, 
        "win%" : single_map_data[1], 
        "wins": single_map_data[2],
        "losses": single_map_data[3], 
        "atk_1st": single_map_data[4], 
        "def_1st": single_map_data[5], 
        "atk_rwin%": single_map_data[6], 
        "atk_rw": single_map_data[7], 
        "atk_rl": single_map_data[8],
        "def_rwin%": single_map_data[9], 
        "def_rw": single_map_data[10], 
        "def_rl": single_map_data[11], 
        }
        
        single_map_dict["agent_compositions"] = []
        #obtaining the agent composition 
        team_composition_scrape = row.find_all("div", class_="agent-comp-agg mod-first")
        for team_composition in team_composition_scrape:
            #getting the amt played for team composition
            team_composition_text = team_composition.get_text().strip()
            team_composition_amt = re.search(r'\d+', team_composition_text)
            if team_composition_amt:
                team_composition_amt = team_composition_amt.group()
            else:
                print("No digits found.")


            img_tags = team_composition.find_all('img', {'src': re.compile(r'/agents/')})
            agents = [re.search(r'/agents/(\w+)\.png', img_tag['src']).group(1) for img_tag in img_tags]
            single_map_dict["agent_compositions"].append({
            "composition": agents,
            "times_used": team_composition_amt
        })
            
        #obtaining the toggled data
        single_map_dict["game_history"] = []
        game_history_scrapes = soup.find_all("tr", class_= f"mod-toggle mod-{map_name}")
        for match_data in game_history_scrapes:
            #extracting the data
            link_html = match_data.find("a")
            link = "vlr.gg" + link_html.get("href")
            match_htmls = match_data.find_all("div")
            match_stat_list = [match_html.get_text().strip() for match_html in match_htmls if "\t" not in match_html.get_text().strip()
                               and match_html.get_text().strip() != ''
                               and match_html.get_text().strip() != "def"
                                and match_html.get_text().strip() != "atk"
                                and match_html.get_text().strip() != "OT"]
            
            single_match_img_tags = match_data.find_all('img', {'src': re.compile(r'/agents/')})
            single_match_agents = [re.search(r'/agents/(\w+)\.png', img_tag['src']).group(1) for img_tag in single_match_img_tags]
            
            single_match_dict = {
                "date": match_stat_list[0],
                "opponent" : match_stat_list[1],
                "total_score" : match_stat_list[3], 
                "atk_score": match_stat_list[4],
                "def_score": match_stat_list[5],
                "ot_score": match_stat_list[6] if len(match_stat_list) ==9 else "na",
                "stage": match_stat_list[-1],
                "week": match_stat_list[-2],
                "team_composition": single_match_agents
            }
            single_map_dict["game_history"].append(single_match_dict)
            
        
        data_list.append(single_map_dict)
        single_map_data=[] 
        
   
    #making it into json data
    jsondata = json.dumps(data_list, indent=4)
    return jsondata

def scrapeIndividualPlayer (playerID: str="", timespan: str=""):#timespan sould be 30d, 60d, 90d, all
    url = f"https://www.vlr.gg/player/{playerID}/?timespan={timespan}"
    print(f" url : {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    
    player_stat_data = []

    table = soup.find("table", class_="wf-table")
    body = table.find("tbody")
    rows = body.find_all("tr")
    for row in rows:
        #getting the agent name
        img_tag = row.find('img', {'src': re.compile(r'/agents/')})
        agent = re.search(r'/agents/(\w+)\.png', img_tag['src']).group(1)
        
        #getting the data 
        stats_html_list = row.find_all("td")
        stats_list = [stat.get_text().strip() for i,stat in enumerate(stats_html_list) if i != 0]
        #sorting through (x)y%
        userate = stats_list[0]
        userate_split = userate.split(" ")
        num_played =re.search(r'\((\d+)\)', userate_split[0])
        num_played= num_played.group(1)
        
        
        player_stat_dict = {
            "agent": agent,
            "games_played": num_played, 
            "agent_pickrate": userate_split[1], 
            "rounds": stats_list[1],
            "ratings" : stats_list[2], 
            "acs": stats_list[3], 
            "kd": stats_list[4], 
            "adr" : stats_list[5], 
            "kast": stats_list[6], 
            "kpr": stats_list[7], 
            "apr": stats_list[8], 
            "fkpr": stats_list[9], 
            "fdpr": stats_list[10], 
            "k": stats_list[11], 
            "d": stats_list[12],
            "a": stats_list[13], 
            "fk": stats_list[14],
            "fd": stats_list[15]
        }
        
        player_stat_data.append(player_stat_dict)

    jsondata = json.dumps(player_stat_data, indent=4)
    return jsondata


def scrapeIndividualMatchData (gameID: str=""):
    url = f"https://www.vlr.gg/{gameID}/?game=all&tab=overview"
    print(f"url: {url}")
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    
    html_body = soup.find("div", class_="vm-stats")
    
    #first scraping the overview data
    game_stats = {
        "match_info": {},
        "box_scores": {}
    } 
    #all maps stats
    # All maps stats
    web_body_html = html_body.find_all("div", class_="vm-stats-game")
    for map_html in web_body_html: 
        map_id = map_html.get('data-game-id')
        if map_id == "all":
            # Initialize the map stats
            if map_id not in game_stats:
                game_stats["box_scores"][map_id] = {"both": [], "attack": [], "defense": []}
            
            table_body_htmls = map_html.find_all("tbody")
            for table_body_html in table_body_htmls:
                rows = table_body_html.find_all("tr")
                
                for row in rows:
                    overview_data_html = row.find_all("td")
                    overview_data_list = [overview_data.get_text().strip().replace("\t", "").split("\n") for overview_data in overview_data_html if overview_data.get_text().strip() != ""]
                    
                    if not overview_data_list:
                        continue
                    
                    # Cleaning the data
                    cleaned_overview_data_list = []
                    for data_list in overview_data_list:
                        cleaned_list = [item.strip() for item in data_list if item.strip() != "" and item.strip() != "/"]
                        if cleaned_list:
                            cleaned_overview_data_list.append(cleaned_list)

                    # Forming the dictionary for each row
                    side_keys = ["both", "attack", "defense"]
                    for side_index, side_key in enumerate(side_keys):
                        player_stats = {
                            "name": cleaned_overview_data_list[0][0],
                            "team": cleaned_overview_data_list[0][1],
                            "rating": cleaned_overview_data_list[1][side_index],
                            "acs": cleaned_overview_data_list[2][side_index],
                            "kills": cleaned_overview_data_list[3][side_index],
                            "deaths": cleaned_overview_data_list[4][side_index],
                            "assists": cleaned_overview_data_list[5][side_index],
                            "plus_minus": cleaned_overview_data_list[6][side_index],
                            "kast": cleaned_overview_data_list[7][side_index],
                            "adr": cleaned_overview_data_list[8][side_index],
                            "hs_percentage": cleaned_overview_data_list[9][side_index],
                            "first_kills": cleaned_overview_data_list[10][side_index],
                            "first_deaths": cleaned_overview_data_list[11][side_index],
                            "plus_minus_overall": cleaned_overview_data_list[12][side_index]
                        }
                        game_stats["box_scores"][map_id][side_key].append(player_stats)

            continue
        
        
        #time for individual maps
        map_name_html = map_html.find("div", class_= "map")
        map_name_html2 = map_name_html.find_all("span")
        map_details = [map_detail.get_text().replace("\t", "").replace("PICK", "").strip() for map_detail in map_name_html2 if map_detail.get_text().replace("\t", "").replace("PICK", "").strip() != ""]
        
        game_stats["box_scores"][map_details[0]] = {"both": [], "attack": [], "defense": []}
        
        #essentially doing the same thing that i did for all map
        table_body_htmls = map_html.find_all("tbody")
        for table_body_html in table_body_htmls:
            rows = table_body_html.find_all("tr")
            
            for row in rows:
                overview_data_html = row.find_all("td")
                overview_data_list = [overview_data.get_text().strip().replace("\t", "").split("\n") for overview_data in overview_data_html if overview_data.get_text().strip() != ""]
                
                if not overview_data_list:
                    continue
                
                # Cleaning the data
                cleaned_overview_data_list = []
                for data_list in overview_data_list:
                    cleaned_list = [item.strip() for item in data_list if item.strip() != "" and item.strip() != "/"]
                    if cleaned_list:
                        cleaned_overview_data_list.append(cleaned_list)

                # Forming the dictionary for each row
                side_keys = ["both", "attack", "defense"]
                for side_index, side_key in enumerate(side_keys):
                    player_stats = {
                        "name": cleaned_overview_data_list[0][0],
                        "team": cleaned_overview_data_list[0][1],
                        "rating": cleaned_overview_data_list[1][side_index],
                        "acs": cleaned_overview_data_list[2][side_index],
                        "kills": cleaned_overview_data_list[3][side_index],
                        "deaths": cleaned_overview_data_list[4][side_index],
                        "assists": cleaned_overview_data_list[5][side_index],
                        "plus_minus": cleaned_overview_data_list[6][side_index],
                        "kast": cleaned_overview_data_list[7][side_index],
                        "adr": cleaned_overview_data_list[8][side_index],
                        "hs_percentage": cleaned_overview_data_list[9][side_index],
                        "first_kills": cleaned_overview_data_list[10][side_index],
                        "first_deaths": cleaned_overview_data_list[11][side_index],
                        "plus_minus_overall": cleaned_overview_data_list[12][side_index]
                    }
                    game_stats["box_scores"][map_details[0]][side_key].append(player_stats)
    
        #general info time!!!
        game_stats["box_scores"][map_details[0]]["general_info"] = {}
        
        general_info_html = map_html.find("div", class_="vm-stats-game-header")
        teams = [general_info_html.find("div", class_="team"), general_info_html.find("div", class_="team mod-right")]
        for i, team in enumerate(teams): 
            general_stats_html = team.find_all("div")
            general_stats_list = [general_stat.get_text().replace("\t", "").replace("/", "").replace(" ", "").strip().split("\n") for general_stat in general_stats_html]
            cleaned_general_stats_list = [[item for item in sublist if item != ''] for sublist in general_stats_list]
            if i % 2 == 0:
                game_stats["box_scores"][map_details[0]]["general_info"][cleaned_general_stats_list[1][0]] = {
                        "score" : cleaned_general_stats_list[0][0], 
                        "halves": {
                            "first_half": cleaned_general_stats_list[1][1],
                            "second_half" : cleaned_general_stats_list[1][2], 
                            "overtime": cleaned_general_stats_list[1][3] if len(cleaned_general_stats_list[1]) == 4 else "na", 
                        }     
                    }
            else:
                game_stats["box_scores"][map_details[0]]["general_info"][cleaned_general_stats_list[1][0]] = {
                        "score" : cleaned_general_stats_list[2][0], 
                        "halves": {
                            "first_half": cleaned_general_stats_list[0][1],
                            "second_half" : cleaned_general_stats_list[0][2], 
                            "overtime": cleaned_general_stats_list[0][3] if len(cleaned_general_stats_list[1]) == 4 else "na", 
                        }     
                    }
                
    jsondata = json.dumps(game_stats, indent=4)
    #print(jsondata)
    return jsondata
    
    
    
    
scrapeIndividualMatchData(gameID= "327267")