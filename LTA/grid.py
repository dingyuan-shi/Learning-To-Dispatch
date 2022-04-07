import math
import pickle
import sys
from typing import Tuple
if sys.platform == 'darwin':
    from model.utils import get_path, acc_dist
    from model.global_var import INF
else:
    from utils import get_path, acc_dist
    from global_var import INF

div_quantile = 2000


class Grid:
    grids = pickle.load(open(get_path(__file__, "grids_info"), "rb"))
    grid_ids = pickle.load(open(get_path(__file__, "grid_id"), "rb"))
    kdtree = pickle.load(open(get_path(__file__, "kdtree"), "rb"))
    min_lng, min_lat, max_lng, max_lat = 200, 200, 0, 0
    for grid_id in grids:
        lng, lat = grids[grid_id]
        min_lng = min(min_lng, lng)
        max_lng = max(max_lng, lng)
        min_lat = min(min_lat, lat)
        max_lat = max(max_lat, lat)
    step_lng = (max_lng - min_lng) / div_quantile
    step_lat = (max_lat - min_lat) / div_quantile
    mesh = [[[] for i in range(div_quantile + 20)] for j in range(div_quantile + 20)]
    for idx, grid_id in enumerate(grid_ids):
        lng, lat = grids[grid_id]
        mesh[int((lng - min_lng) / step_lng) + 1][int((lat - min_lat) / step_lat) + 1].append((idx, grids[grid_id]))
    # for i in range(div_quantile + 20):
    #     for j in range(div_quantile + 20):
    #         if len(mesh[i][j]) > 1:
    #             print(len(mesh[i][j]))
    # print(min_lng, max_lng, min_lat, max_lat, step_lng, step_lat)
    dx = [0, 0, 0, 1, 1, 1, -1, -1, -1]
    dy = [0, 1, -1, 1, 0, -1, 0, 1, -1]

    @staticmethod
    def get_grid_ids():
        return Grid.grid_ids

    @staticmethod
    def _find_grid(lng: float, lat: float) -> Tuple[str, int]:
        _, i = Grid.kdtree.query([lng, lat])
        return Grid.grid_ids[i], i

    @staticmethod
    def find_grid(lng: float, lat: float) -> Tuple[str, int]:
        i = int((lng - Grid.min_lng) / Grid.step_lng) + 1
        j = int((lat - Grid.min_lat) / Grid.step_lat) + 1
        min_dis = 10000
        idx = -1
        try:
            for di in range(9):
                for id, lng_lat in Grid.mesh[i + Grid.dx[di]][j + Grid.dy[di]]:
                    dis = (lng - lng_lat[0]) * (lng - lng_lat[0]) + (lat - lng_lat[1]) * (lat - lng_lat[1])
                    # dis = acc_dist(lng, lat, lng_lat[0], lng_lat[1])
                    if min_dis > dis:
                        idx = id
                        min_dis = dis
        except:
            idx = 0
        return Grid.grid_ids[idx], idx

    @staticmethod
    def mahattan_distance(grid_hash0: str, grid_hash1: str) -> float:
        if grid_hash0 in Grid.grids and grid_hash1 in Grid.grids:
            lng0, lat0 = Grid.grids[grid_hash0]
            lng1, lat1 = Grid.grids[grid_hash1]
            delta_lng = 0.685 * abs(lng0 - lng1)
            delta_lat = abs(lat0 - lat1)
            return 111320 * math.sqrt(delta_lat * delta_lat + delta_lng * delta_lng)
        return INF
