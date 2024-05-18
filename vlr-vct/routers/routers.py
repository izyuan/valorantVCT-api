from fastapi import APIRouter, HTTPException
from util.models import PlayerStats, AgentPickrates, TeamStats, IndividualPlayerStats, getIndividualMatchData
from util.dictionaries import teams_dict
import json
router = APIRouter()


def find_team_group(teams_dict, team_id):
    """
    Find and return the sub-dictionary from teams_dict where team_id is a value.
    
    Args:
    teams_dict (dict): A dictionary of sub-dictionaries, where each sub-dictionary
                       represents a group of teams with their respective IDs.
    team_id (str): The team ID to search for in the teams_dict.

    Returns:
    dict: The sub-dictionary containing the team_id, or None if not found.
    """
    for group_name, teams in teams_dict.items():
        if team_id == group_name:
            return teams
    return None

@router.get("/player_stats")
async def getPlayerStats (data:PlayerStats):
    from data.webscraping import scrapePlayerStats
    response = scrapePlayerStats(
    regionID=data.regionID, 
    eventSeries=data.eventSeries,
    eventID= data.eventID, 
    agent=data.agent, 
    minRounds= data.minRounds, 
    minRating= data.minRating, 
    mapID= data.mapID, 
    timespan= data.timespan
    )
    return response
    
@router.get("/agent_pickrates") #remind me to change to two seperate "map rates" and "agent rates"
async def getAgentPickrates (data: AgentPickrates):
    from data.webscraping import scrapeAndMapAgentStats
    response = scrapeAndMapAgentStats(event=data.event)
    return response
    
    
@router.get("/team_statistics")
async def getTeamStats (data:TeamStats): 
    from data.webscraping import scrapeTeamStats
    response = scrapeTeamStats(
        team= data.teamID, 
        event= data.event, 
        core=data.core,
        date_start=data.date_start,
        date_end= data.date_end
    )
    return response

@router.get("/all_team_statistics")
async def getAllTeamStats(data: TeamStats):
    from data.webscraping import scrapeTeamStats
    all_team_stats = []
    dictionary_to_use = find_team_group(teams_dict, data.teamID)
    if dictionary_to_use is None:
        print(f"No team found with ID {data.teamID}")
        return [] 
    for team_name, team_id in dictionary_to_use.items():
        try:
            response = scrapeTeamStats(
                team=team_id,  # Use the team ID from the dictionary
                event=data.event,
                core=data.core,
                date_start=data.date_start,
                date_end=data.date_end
            )
            team_stats = json.loads(response)
            all_team_stats.extend(team_stats)
        except Exception as e:
            print(f"Failed to retrieve stats for {team_name}: {str(e)}")
    
    return all_team_stats

@router.get("/individual_player_stats")
async def getIndividualStats (data: IndividualPlayerStats):
    from data.webscraping import scrapeIndividualPlayer
    response = scrapeIndividualPlayer(
        playerID=data.playerID, 
        timespan=data.timespan
    )
    return response

@router.get("/individual_match_data")
async def getIndividualMatchData (data: getIndividualMatchData):
    from data.webscraping import scrapeIndividualMatchData
    response = scrapeIndividualMatchData(
        gameID= data.gameID, 
    )
    return response