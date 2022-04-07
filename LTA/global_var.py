MIN_PER_HOUR = 60
alpha = 0.025
gamma1 = 0.9
residual = 0.09
gamma2 = gamma1 + residual
time_step = 2
lng_step = 0.003
lat_step = 0.003
# DIRS = [[0, 0], [0, 1], [1, 0], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
DIRS = [[3, 1], [1, -3], [-3, -1], [-1, 3], [0, 0]]
# DIRS = [[0, 0], [0, 1], [1, 0], [0, -1], [-1, 0]]
DIR_NUM = len(DIRS)
SPEED = 3
INF = 1e12
QUICK = True       # True: use probability quick version
INIT_VALUE = False

INIT_GRID = False # initial values for grid values
TIME_INTERVAL = 10 * 60

IS_CLEAR = True # clear up the values when day_of_week changes

