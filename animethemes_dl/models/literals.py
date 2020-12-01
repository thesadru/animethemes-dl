"""
Literals of animethemes-dl.
"""
from typing import Literal, NewType

Score = Literal[0,1,2,3,4,5,6,7,8,9]
Priority = Literal[0,1,2]
Status = Literal[1,2,3,4,6]

UrlLike = str
DateLike = NewType('DateLike',str)
Types = Literal['OP','ED']
Season = Literal['Spring','Summer','Fall','Winter']
ImageFacet = Literal["Large Cover","Small Cover"]
