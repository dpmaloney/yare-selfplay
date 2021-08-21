from gym.envs.registration import register

register(
    id='Yare-v0',
    entry_point='yare.envs:YareEnv',
)

