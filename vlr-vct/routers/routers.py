from fastapi import APIRouter
from util.models import PlayerStats

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
    
