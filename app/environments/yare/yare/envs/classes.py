import random
from ctypes import *

class Vec2(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float)]


# result = -1 (game still on going)
#           0 player 0 won
#           1 player 1 won
#           2 draw (game timed out)
class SimResult(Structure):
    _fields_ = [("tick", c_uint),
                ("result", c_int)]

class Id(Structure):
    _fields_ = [("player_id", c_uint),
                ("index", c_uint)]

TICKFN = CFUNCTYPE(None, c_ulong)
