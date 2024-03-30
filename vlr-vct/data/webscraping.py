import requests
from bs4 import BeautifulSoup
from lxml import html
import json

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
    "2543" : ["champions 2023", "Champions 2023"]
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

def scrapePlayerStats (regionID: str="all", eventSeries: str="61", eventID: int="all", minRounds: int="all", minRating: int="all", agent:str="all", mapID: str="all", timespan:int=60): #61 for franchising valorant,
    """get the stats of players

    Args:
        each param is a filter essentially 
    """
    region = getKey(vlrregionDict, regionID) or regionID
    map = getKey(vlrmapDict, mapID) or mapID
    Timespan = getKey(vlrtimestampDict, timespan) or timespan
    
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
        print(stats) 
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
                "rounds_played" : rounds_played,
                "average_combat_score": average_combat_score,
                "kill_death_ratio": kill_death_ratio, 
                "kills_assists_survived_traded": kast,
                "average_damage_per_round": average_damage_per_round,
                "kills_per_round": kills_per_round,
                "assists_per_round": assists_per_round,
                "first_kills_per_round": first_kills_per_round,
                "first_deaths_per_round": first_deaths_per_round,
                "headshot_percentage": headshot_percentage,
                "clutch_success_percentage": clutch_success_percentage,
                "clutch_fraction": clutch_fraction,
                "kill_max" : kill_max_value,
                "total_kills" : total_kills,
                "total_deaths": total_deaths,
                "total_assists": total_assists, 
                "total_first_kills" : total_first_kills, 
                "total_first_deaths" : total_first_deaths
            })
        except:
            return {"status": "failed"}

    data = {"players_stats": players_stats}

    return data
  
  
def scrapeAgentStats (): 
    import json
    url = f"https://www.vlr.gg/event/agents/1921/"
    response = requests.get(url)
    
    soup = BeautifulSoup(response.content, 'lxml')
    row = soup.find('tr', class_='pr-global-row')
    map_data = {}

    for td in row.find_all('td'):
        if 'mod-right' in td.get('class', []):
            key = td.get_text().strip()
            map_data[key] = td.get_text().strip()
        elif 'mod-color-sq' in td.get('class', []):
            color_sq = td.find('div', class_='color-sq')
            if color_sq:
                span = color_sq.find('span')
                if span:
                    value = span.get_text().strip()
                    
    json_data = json.dumps(map_data, indent=4)
    print(json_data)
    
scrapeAgentStats()
