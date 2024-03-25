from pydantic import BaseModel, Field

class PlayerStats(BaseModel):
    regionID: str = Field(default="all", alias='regionID')
    eventSeries: int = Field(default=61, alias='Major League')
    eventID: str = Field(default="all", alias='Major Event')
    agent: str = Field(default="all", alias='Agent')
    minRounds: str = Field(default="all", alias='Minimum Rounds')
    minRating: str = Field(default="all", alias='Minimum Rating')
    mapID: str = Field(default="all", alias='mapID')
    timespan: str = Field(default="60", alias='timespan')
    class Config:
        populate_by_name = True
