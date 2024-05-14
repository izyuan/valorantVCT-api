from pydantic import BaseModel, Field

class PlayerStats(BaseModel):
    regionID: str = Field(default="all", alias='regionID')
    eventSeries: str = Field(default=61, alias='Major League')
    eventID: str = Field(default="all", alias='Major Event')
    agent: str = Field(default="all", alias='Agent')
    minRounds: str = Field(default="all", alias='Minimum Rounds')
    minRating: str = Field(default="all", alias='Minimum Rating')
    mapID: str = Field(default="all", alias='mapID')
    timespan: str = Field(default="60", alias='timespan')
    class Config:
        populate_by_name = True

class AgentPickrates (BaseModel):
    event : str= "1921"
    
class TeamStats (BaseModel):
    teamID : str="all"
    event : str = "all"
    core:str="all"
    date_start: str=""
    date_end:str=""
    
class IndividualPlayerStats (BaseModel): 
    playerID: str=""
    timespan: str=""