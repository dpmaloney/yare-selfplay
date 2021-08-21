
import gym
import numpy as np

import config

from stable_baselines3.common.logger import Logger

from ctypes import *
from ctypes.util import find_library
from ctypes import wintypes
import pathlib

import itertools

import math

from .classes import *

class YareEnv(gym.Env):
    metadata = {'render.modes': ['human']}

        

    def __init__(self, verbose = False, manual = False):
        super(YareEnv, self).__init__()
        self.name = 'yare'
        self.manual = manual
        self.n_players = 2
        self.current_player_num = 0
        self.ticks = 0
        self.done = False


        libname = pathlib.Path().absolute() / "yareio.dll"
        botpath = pathlib.Path().absolute() / "libbot.dll"

        self.lib = WinDLL(name=str(libname))
        self.bot = WinDLL(name=str(botpath))

        self.lib.headless_simulate.argtypes = [TICKFN, c_uint, TICKFN, c_uint]
        self.lib.headless_simulate.restype = SimResult
        self.lib.headless_init.argtypes = [TICKFN, c_uint, TICKFN, c_uint, c_char_p]
        self.lib.headless_init.restype = c_void_p
        self.lib.headless_update_env.argtypes = [c_void_p]
        self.lib.headless_update_env.restype = None
        self.lib.headless_gather_commands.argtypes = [c_void_p, c_uint]
        self.lib.headless_gather_commands.restype = None
        self.lib.headless_process_commands.argtypes = [c_void_p]
        self.lib.headless_process_commands.restype = SimResult
        self.lib.headless_free.argtypes = [c_void_p]
        self.lib.headless_free.restype = None

        # Spirit Info
        self.lib.spirit_count.argtypes = []
        self.lib.spirit_count.restype = c_uint
        self.lib.spirit_energy.argtypes = [c_uint]
        self.lib.spirit_energy.restype = c_long
        self.lib.spirit_energy_capacity.argtypes = [c_uint]
        self.lib.spirit_energy_capacity.restype = c_long
        self.lib.spirit_hp.argtypes = [c_uint]
        self.lib.spirit_hp.restype = c_ulong
        self.lib.spirit_id.argtypes = [c_uint]
        self.lib.spirit_id.restype = Id
        self.lib.spirit_position.argtypes = [c_uint]
        self.lib.spirit_position.restype = Vec2
        self.lib.spirit_shape.argtypes = [c_uint]
        self.lib.spirit_shape.restype = c_uint
        self.lib.spirit_size.argtypes = [c_uint]
        self.lib.spirit_size.restype = c_long


        # Commands
        self.lib.spirit_energize_base.argtypes = [c_uint, c_uint]
        self.lib.spirit_energize_base.restype = None
        self.lib.spirit_energize_outpost.argtypes = [c_uint, c_uint]
        self.lib.spirit_energize_outpost.restype = None
        self.lib.spirit_energize.argtypes = [c_uint, c_uint]
        self.lib.spirit_energize.restype = None
        self.lib.spirit_goto.argtypes = [c_uint, c_float, c_float]
        self.lib.spirit_goto.restype = None

        # Shape Specific Commands
        self.lib.spirit_explode.argtypes = [c_uint]
        self.lib.spirit_explode.restype = None
        self.lib.spirit_jump.argtypes = [c_uint, c_float, c_float]
        self.lib.spirit_jump.restype = None
        self.lib.spirit_merge.argtypes = [c_uint, c_uint]
        self.lib.spirit_merge.restype = None
        self.lib.spirit_divide.argtypes = [c_uint]
        self.lib.spirit_divide.restype = None

        # Star
        self.lib.star_active_at.argtypes = [c_uint]
        self.lib.star_active_at.restype = c_ulong
        self.lib.star_count.argtypes = []
        self.lib.star_count.restype = c_uint
        self.lib.star_energy_capacity.argtypes = [c_uint]
        self.lib.star_energy_capacity.restype = c_long
        self.lib.star_energy.argtypes = [c_uint]
        self.lib.star_energy.restype = c_long
        self.lib.star_position.argtypes = [c_uint]
        self.lib.star_position.restype = Vec2

        # Outpost
        self.lib.outpost_count.argtypes = []
        self.lib.outpost_count.restype = c_uint
        self.lib.outpost_energy_capacity.argtypes = [c_uint]
        self.lib.outpost_energy_capacity.restype = c_long
        self.lib.outpost_energy.argtypes = [c_uint]
        self.lib.outpost_energy.restype = c_long
        self.lib.outpost_player_id.argtypes = [c_uint]
        self.lib.outpost_player_id.restype = c_uint
        self.lib.outpost_position.argtypes = [c_uint]
        self.lib.outpost_position.restype = Vec2
        self.lib.outpost_range.argtypes = [c_uint]
        self.lib.outpost_range.restype = c_float

        # Base
        self.lib.base_count.argtypes = []
        self.lib.base_count.restype = c_uint
        self.lib.base_current_spirit_cost.argtypes = [c_uint]
        self.lib.base_current_spirit_cost.restype = c_long
        self.lib.base_energy_capacity.argtypes = [c_uint]
        self.lib.base_energy_capacity.restype = c_long
        self.lib.base_energy.argtypes = [c_uint]
        self.lib.base_energy.restype = c_long
        self.lib.base_hp.argtypes = [c_uint]
        self.lib.base_hp.restype = c_ulong
        self.lib.base_player_id.argtypes = [c_uint]
        self.lib.base_player_id.restype = c_uint
        self.lib.base_position.argtypes = [c_uint]
        self.lib.base_position.restype = Vec2

        # Player
        self.lib.player_me.argtypes = []
        self.lib.player_me.restype = c_uint

        self.bot.tick.argtypes = [c_uint, c_bool, c_bool, c_bool, c_bool, c_bool, c_bool, c_bool]
        self.bot.tick.restype = None

        self.bot.tick2.argtypes = [c_uint, c_bool, c_bool, c_bool, c_bool, c_bool, c_bool, c_bool]
        self.bot.tick2.restype = None

        self.p1 = TICKFN(self.player1)
        self.p2 = TICKFN(self.player2)

        self.shape1 = c_uint(0)
        self.shape2 = c_uint(0)

        self.p1attack = False
        self.p1FightOp = False
        self.p1captureOp = False
        self.p1harassBase = False
        self.p1harassStar = False
        self.p1Defend = True
        self.p1DefendStar = True

        self.p2attack = False
        self.p2FightOp = False
        self.p2captureOp = False
        self.p2harassBase = False
        self.p2harassStar = False
        self.p2Defend = True
        self.p2DefendStar = True
        
        self.simulation = self.lib.headless_init(self.p1, self.shape1, self.p2, self.shape2, create_string_buffer(b'replay.json'))
        self.lib.headless_update_env(self.simulation)

        self.action_bank = []

        self.result = -1



        self.action_space = gym.spaces.Discrete(128)
        self.observation_space = gym.spaces.Box(-1, 1, (16 + self.action_space.n ,))
        self.verbose = verbose

    def distance(self, pos1, pos2):
        #print(math.sqrt(math.pow((pos1.x - pos2.x), 2) + math.pow((pos1.y - pos2.y), 2)))
        return math.sqrt(math.pow((pos1.x - pos2.x), 2) + math.pow((pos1.y - pos2.y), 2))

    def player1(self, x):
        self.bot.tick(x, bool(self.p1attack), bool(self.p1FightOp), bool(self.p1captureOp), bool(self.p1harassBase), bool(self.p1harassStar), bool(self.p1Defend), bool(self.p1DefendStar))
        return

    def player2(self, x):
        #print(bool(self.p2attack), bool(self.p2FightOp), bool(self.p2captureOp), bool(self.p2harassBase), bool(self.p2harassStar), bool(self.p2Defend), bool(self.p2DefendStar))
        self.bot.tick2(x, bool(self.p2attack), bool(self.p2FightOp), bool(self.p2captureOp), bool(self.p2harassBase), bool(self.p2harassStar), bool(self.p2Defend), bool(self.p2DefendStar))
        return

        
    @property
    def observation(self):
        #convert currentplaynum to player_id
        np.seterr(all='raise')

        player_id = self.current_player_num
        myEnergyCap = 0
        myEnergy = 0
        myEnergyCapOp = 0
        myEnergyOp = 0
        enemyEng800MyBase = 0
        enemyEng400MyBase  = 0
        myShape = 0

        enemyEnergyCap = 0
        enemyEnergy = 0
        enemyEnergyCapOp = 0
        enemyEnergyOp = 0
        myEng800enemyBase = 0
        myEng400enemyBase  = 0
        enemyShape = 0

        opEng = round(self.lib.outpost_energy(0)/1000, 3)
        opFriendly = 0
        if(self.lib.outpost_player_id(0) == player_id):
            opFriendly = 1
        else:
            opFriendly = -1


        myBaseId = -1
        enemyBaseId = -1
        if(self.lib.base_player_id(0) == player_id):
            myBaseId = 0
            enemyBaseId = 1
        else:
            myBaseId = 1
            enemyBaseId = 0


        for i in range(self.lib.spirit_count()):
            if(self.lib.spirit_id(i).player_id == player_id):
                #friendly spirit
                myEnergyCap += self.lib.spirit_energy_capacity(i)
                myEnergy += self.lib.spirit_energy(i)
                if myShape == 0:
                    myShape = self.lib.spirit_shape(i) - 1

                if(self.distance(self.lib.spirit_position(i), self.lib.outpost_position(0)) < self.lib.outpost_range(0)):
                    myEnergyCapOp += self.lib.spirit_energy_capacity(i)
                    myEnergyOp += self.lib.spirit_energy(i)

                if(self.distance(self.lib.spirit_position(i), self.lib.base_position(enemyBaseId)) < 800):
                    myEng800enemyBase += self.lib.spirit_energy(i)

                if(self.distance(self.lib.spirit_position(i), self.lib.base_position(enemyBaseId)) < 400):
                    myEng400enemyBase += self.lib.spirit_energy(i)
                
                

            else:
                #not friendly spirit
                enemyEnergyCap += self.lib.spirit_energy_capacity(i)
                enemyEnergy += self.lib.spirit_energy(i)
                if enemyShape == 0:
                    enemyShape = self.lib.spirit_shape(i) - 1

                if(self.distance(self.lib.spirit_position(i), self.lib.outpost_position(0)) < self.lib.outpost_range(0)):
                    enemyEnergyCapOp += self.lib.spirit_energy_capacity(i)
                    enemyEnergyOp += self.lib.spirit_energy(i)

                if(self.distance(self.lib.spirit_position(i), self.lib.base_position(myBaseId)) < 800):
                    enemyEng800MyBase += self.lib.spirit_energy(i)

                if(self.distance(self.lib.spirit_position(i), self.lib.base_position(myBaseId)) < 400):
                    enemyEng400MyBase += self.lib.spirit_energy(i)


        out = np.array([round(myEnergyCap/10000, 4),
        round(myEnergy/10000, 4),
        round(myEnergyCapOp/10000, 4),
        round(myEnergyOp/10000, 4),
        round(enemyEng800MyBase/10000, 4),
        round(enemyEng400MyBase/10000, 4),
        myShape,

        round(enemyEnergyCap/10000, 4),
        round(enemyEnergy/10000, 4),
        round(enemyEnergyCapOp/10000, 4),
        round(enemyEnergyOp/10000, 4),
        round(myEng800enemyBase/10000, 4),
        round(myEng400enemyBase/10000, 4),
        enemyShape,

        opEng,
        opFriendly,
        ])

        out = np.append(out, self.legal_actions)

        return out


    @property
    def legal_actions(self):
        return np.ones(128) #list(list(tup) for tup in itertools.product([1,0], repeat=7))

    
    def step(self, action):
        reward = [0, 0]
        self.done = False
        self.action_bank.append(action)
        #print(self.action_bank)

        if len(self.action_bank) == self.n_players:
            #logger.debug(f'\nMaking Moves')
            for i, action in enumerate(self.action_bank):
                todo = list(list(tup) for tup in itertools.product([1,0], repeat=7))
                actionv = todo[action]
                #print(i)
                if i == 0:
                    self.p1attack = bool(actionv[0])
                    self.p1captureOp = bool(actionv[1])
                    self.p1fightOp = bool(actionv[2])
                    self.p1DefendStar = bool(actionv[3])
                    self.p1harassBase= bool(actionv[4])
                    self.p1harassStar = bool(actionv[5])
                    self.p1Defend = bool(actionv[6])
                else:
                    self.p2attack = bool(actionv[0])
                    self.p2captureOp = bool(actionv[1])
                    self.p2fightOp = bool(actionv[2])
                    self.p2DefendStar = bool(actionv[3])
                    self.p2harassBase= bool(actionv[4])
                    self.p2harassStar = bool(actionv[5])
                    self.p2Defend = bool(actionv[6])

            self.action_bank = []

            self.lib.headless_update_env(self.simulation)
            self.lib.headless_gather_commands(self.simulation, c_uint(0))
            self.lib.headless_gather_commands(self.simulation, c_uint(1))
            res = self.lib.headless_process_commands(self.simulation)
            self.result = res.result
            if self.result >= 0:
                self.done = True
                if res.result == 0:
                    reward[0] = 1
                    reward[1] = -1
                elif res.result == 1:
                    reward[1] = 1
                    reward[0] = -1
                else:
                    reward[0] = -.5
                    reward[1] = -.5
            else:
                for i in range(self.lib.spirit_count()):
                    if(self.lib.spirit_id(i).player_id == 0):
                        reward[0] = reward[0] + round(self.lib.spirit_energy_capacity(i)/10000, 4)
                        reward[1] = reward[1] - round(self.lib.spirit_energy_capacity(i)/10000, 4)
                    else:
                        reward[1] = reward[1] + round(self.lib.spirit_energy_capacity(i)/10000, 4)
                        reward[0] = reward[0] - round(self.lib.spirit_energy_capacity(i)/10000, 4)

        
                

        reward = [round(reward[0], 4) ,round(reward[1], 4)]
        self.current_player_num = (self.current_player_num + 1) % self.n_players

        if self.current_player_num == 0:
            self.ticks += 1

        return self.observation, reward, self.done, {}


    

    def reset(self):
        self.lib.headless_free(self.simulation)
        self.simulation = None

        self.simulation = self.lib.headless_init(self.p1, self.shape1, self.p2, self.shape2, create_string_buffer(b'replay.json'))
        self.lib.headless_update_env(self.simulation)

        self.current_player_num = 0
        self.ticks = 0
        self.done = False

        self.p1attack = False
        self.p1FightOp = False
        self.p1captureOp = False
        self.p1harassBase = False
        self.p1harassStar = False
        self.p1Defend = True
        self.p1DefendStar = True

        self.p2attack = False
        self.p2FightOp = False
        self.p2captureOp = False
        self.p2harassBase = False
        self.p2harassStar = False
        self.p2Defend = True
        self.p2DefendStar = True

        self.action_bank = []

        self.result = -1

        #logger.debug(f'\n\n---- NEW GAME ----')
        return self.observation


    def render(self, mode='human', close=False):
        return
