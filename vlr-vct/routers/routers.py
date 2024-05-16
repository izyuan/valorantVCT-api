from fastapi import APIRouter
from util.models import PlayerStats, AgentPickrates, TeamStats, IndividualPlayerStats, getIndividualMatchData

router = APIRouter()

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