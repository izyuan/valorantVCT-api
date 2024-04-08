from fastapi import APIRouter
from util.models import PlayerStats, AgentPickrates

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
    