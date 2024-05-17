import json

def merge_dicts(*dicts):
    merged_dict = {}
    for d in dicts:
        merged_dict.update(d)
    return merged_dict


event_series_id = {
    "Valorant Champions Tour 2024" : "61",
    "Valorant Champions Tour 2023" : "45",
    "Valorant Champions Tour 2022" : "14",
    "Valorant Champions Tour 2021" : "3"
    
}

event_id = {
    "Masters Madrid" : "1921"
}

all_teams = {
    "100 Thieves": "120",
    "G2 Esports": "11058",
    "Leviaten": "2359",
    "Kru Esports": "2355",
    "Cloud9": "188",
    "Loud": "6961",
    "Sentinels": "2",
    "NRG Esports": "1034",
    "Evil Geniuses": "5248",
    "Mibr": "7386",
    "Furia": "2406",
    "FNATIC": "2593",
    "Karmine Corp": "8877",
    "Team Heretics": "1001",
    "FUT Esports": "1184",
    "Natus Vincere": "4915",
    "BBL Esports": "397",
    "Team Vitality": "2059",
    "Team Liquid": "474",
    "Gentle Mates": "12694",
    "GIANTX": "14419",
    "KOI": "7035",
    "Paper Rex": "624",
    "Gen.G": "17",
    "DRX": "8185",
    "T1": "14",
    "Talon Esports": "8304",
    "Rex Regum Qeon": "878",
    "Team Secret": "6199",
    "Global Esports": "918",
    "Zeta Division": "5448",
    "Bleed": "6387",
    "DFM": "278",
    "Edward Gaming": "1120",
    "FunPlus Phoenix": "11328",
    "Dragon Ranger Gaming": "11981",
    "Trace Esports": "12685",
    "All Gamers": "1119",
    "Bilibili Gaming": "12010",
    "TYLOO": "731",
    "Wolves Esports": "13790",
    "Titan Esports Club": "14137",
    "Nova Esports": "12064",
    "JD Gaming": "13576"
}


americas_teams = {
 "100 Thieves" : "120",
 "G2 Esports" : "11058",
 "Leviaten" : "2359",
 "Kru Esports": "2355", 
 "Cloud9": "188", 
 "Loud": "6961",
 "Sentinels": "2",
 "NRG Esports": "1034", 
 "Evil Geniuses": "5248",
 "Mibr": "7386",
 "Furia": "2406", 
 }

pacific_teams = {
    "Paper Rex" : "624", 
    "Gen.G": "17", 
    "DRX": "8185",
    "T1": "14",
    "Talon Esports": "8304",
    "Rex Regum Qeon": "878", 
    "Team Secret": "6199",
    "Global Esports": "918", 
    "Zeta Division": "5448",
    "Bleed": "6387", 
    "DFM": "278"
}

emea_teams ={
    "FNATIC" : "2593", 
    "Karmine Corp" : "8877", 
    "Team Heretics" : "1001", 
    "FUT Esports" : "1184", 
    "Natus Vincere" : "4915", 
    "BBL Esports" : "397", 
    "Team Vitality" : "2059", 
    "Team Liquid" : "474", 
    "Gentle Mates": "12694", 
    "GIANTX" : "14419", 
    "KOI": "7035", 
}

china_teams = {
    "Edward Gaming" : "1120", 
    "FunPlus Phoenix" : "11328", 
    "Dragon Ranger Gaming" : "11981", 
    "Trace Esports" : "12685", 
    "All Gamers" : "1119", 
    "Bilibili Gaming" : "12010", 
    "TYLOO" : "731", 
    "Wolves Esports": "13790",
    "Titan Esports Club": "14137", 
    "Nova Esports" : "12064", 
    "JD Gaming": "13576"
 }

print(json.dumps(merge_dicts(americas_teams, emea_teams, pacific_teams, china_teams),indent=4))

