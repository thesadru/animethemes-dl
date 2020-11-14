from typing import Literal, NewType

UrlLike = str
Priority = Literal[0,1,2]
Score = Literal[0,1,2,3,4,5,6,7,8,9,10]
Season = Literal['spring','summer','fall','winter']
Status = Literal[1,2,3,4,6]
StrInt =  NewType('str[int]',str)
