import random
from math import ceil
from time import process_time
import numpy as np
from abc import ABC, abstractmethod
from .Coords import Coords
from ..utils.FileUtil import write_sgems_file
from ..utils.utility import threeD_to_1D, oneD_to_3D, is_nan, secondsToHrMnSec
from ..utils import Etype
from ..utils import MDS


class MPSAlgorithm(ABC):

    def __init__(self):
        """
        构造函数
        """
        print("1:成功继承")
        self._sg = []  # The simulation grid
        self._hdg = []  # The hard data grid (same size as simulation grid)
        self._tg1 = []  # Temporary grid 1 - meaning define by type of sim-algorithm (same size as simulation grid)
        self._tg2 = []  # Temporary grid 2 - meaning define by type of sim-algorithm (same size as simulation grid)
        self._hd_search_radius = 0.0  # hard data search radius for multiple grids
        self._sg_iterations = []  # 用于调试的模拟网格的副本，用于计算迭代次数
        self._simulation_path = []  # The simulation path
        self._total_grids_level = 0  # multiGrids  levels
        self._sg_dim_x = 0  # Dimension X of the simulation Grid
        self._sg_dim_y = 0  # Dimension Y of the simulation Grid
        self._sg_dim_z = 0  # Dimension Z of the simulation Grid
        self._sg_world_min_x = 0.0  # Coordinate X Min of the simulation grid in world coordinate
        self._sg_world_min_y = 0.0  # Coordinate Y Min of the simulation grid in world coordinate
        self._sg_world_min_z = 0.0  # Coordinate Z Min of the simulation grid in world coordinate
        self._sg_cell_size_x = 0.0  # 在坐标系中x轴方向的单元格大小
        self._sg_cell_size_y = 0.0  # 在坐标系中Y轴方向的单元格大小
        self._sg_cell_size_z = 0.0  # 在坐标系中Z轴方向的单元格大小
        self._max_cond_data = 0  # Maximum conditional data allowed
        self._shuffle_sg_path = 0  # Define type of random simulation grid path
        self._shuffle_entropy_factor = 0  # 定义随机模拟路径的熵因子
        self._realization_numbers = 0  # 创建实现数量
        '''
        * @ brief
        如果在调试模式下，将创建一些额外的文件和信息
        *可以使用不同级别的调试：
        *-1: 没有信息
        *0: 在控制台上显示已用时间
        *1: 在控制台上有网格预览
        *2: 额外的文件被导出（迭代计数器）到输出文件夹
        '''
        self._debug_mode = 0
        self._self_show_preview = False  # Show the simulation grid result in the console
        self._seed = 0.0  # Initial value of the simulation
        self._max_iterations = 0  # 最大迭代次数
        self._ti_dim_x = 0  # Dimension X of the training image
        self._ti_dim_y = 0  # Dimension Y of the training image
        self._ti_dim_z = 0  # Dimension Z of the training image
        self._max_neighbours = 0  # Maximum neighbour allowed when doing the neighbour search function
        self._shuffle_ti_path = True  # Make a random training image path
        self._ti_path = []  # Training image search path
        self._number_of_threads = 0  # Maximum threads used for the simulation
        self._ti_filename = ""  # Training image's filename
        self._output_directory = ""  # Output directory to store the result
        self._hardData_filenames = ""  # Hard data filenames used for the simulation
        self._softData_filenames = [""]  # Soft data filenames used for the simulation
        self._softData_categories = []  # Soft data categories
        self._softData_grids = []  # SoftData grid
        self._TI = []  # The training image
        self._threads = []  # 线程
        self._job_done = False  # 用于同步线程的原子标志

    @abstractmethod
    def _simulate(self, sg_idx_x, sg_idx_y, sg_idx_z, level):
        """
        在MPSAlgorithm类里面的虚函数，本身并未实现，通过子类SNESIMTree重写后调用
        :param sg_idx_x:
        :param sg_idx_y:
        :param sg_idx_z:
        :param level:
        :return:
        """


    @abstractmethod
    def _InitStartSimulationEachMultipleGrid(self, level):
        """
        在MPSAlgorithm类里面的虚函数，本身并未实现，通过子类SNESIMTree重写后调用
        :param level:
        :return:
        """


    def _fillSGfromHD(self, x, y, z, level, add_nodes, putback_nodes):
        """
        为粗网格执行硬数据重定位
        :param x:待模拟点坐标
        :param y:待模拟点坐标
        :param z:待模拟点坐标
        :param level:多重网格级数
        :param add_nodes:已重定位点列表，方便清除
        :param putback_nodes:待放回列表，清除后放回
        :return:
        """

        """
        多重网格的使用会影响条件模拟中条件点的写入：
        如果直接写入条件数据到模拟网格，由于最外层网格粒度太大可能会忽略掉条件点，
        导致条件点很难对于整体结构的构建起到约束效果。因此采用一种数据重定位的方式：
        在粗粒度网格模拟时，将条件数据写到最近的粗网格节点上，条件点的值清空，
        在模拟结束后去除掉写入了粗网格节点的重定位数据，还原条件点的值。
        """

        # 判断：如果硬数据存在，且当前待模拟的网格为空，执行硬数据重定位
        if len(self._hdg) != 0 and is_nan(self._sg[z][y][x]):
            # 声明一个点对象来存放邻居节点
            # 邻居节点即在搜索半径内的硬数据节点
            closestCoords = Coords(0, 0, 0)

            # 判断：如果邻居节点存在
            if self._IsClosedToNodeInGrid(x, y, z, level, self._hdg, ceil(pow(2, level) / 2), closestCoords):
                # 邻居节点 加入 待放回列表
                putback_nodes.append(closestCoords)
                # 当前模拟节点 加入 已重定位点列表
                add_nodes.append(Coords(x, y, z))
                # 邻居节点的值 赋给 当前模拟节点
                self._sg[z][y][x] = self._hdg[closestCoords.getZIndex()][closestCoords.getYIndex()][
                    closestCoords.getXIndex()]
                # 邻居节点的值 暂时清除
                self._hdg[closestCoords.getZIndex()][closestCoords.getYIndex()][closestCoords.getXIndex()] = np.nan

    def _clearSGFromHD(self, add_nodes, putback_nodes):
        """
        重定位数据的还原
        :param add_nodes: 已重定位点列表，存放重定位目标点坐标
        :param putback_nodes: 待放回列表，存放重定位原点坐标
        :return:
        """

        for i in range(0, len(add_nodes)):
            # 把重定位的数据还原回去
            self._hdg[putback_nodes[i].getZIndex()][putback_nodes[i].getYIndex()][putback_nodes[i].getXIndex()] \
                = self._sg[add_nodes[i].getZIndex()][add_nodes[i].getYIndex()][add_nodes[i].getXIndex()]

            # 判断：重定位的如果是
            if add_nodes[i].getZIndex() != putback_nodes[i].getZIndex() and add_nodes[i].getYIndex() != putback_nodes[
                i].getYIndex() \
                    and add_nodes[i].getXIndex() != putback_nodes[i].getXIndex():
                self._sg[add_nodes[i].getZIndex()][add_nodes[i].getYIndex()][add_nodes[i].getXIndex()] = np.nan

        add_nodes.clear()
        putback_nodes.clear()

    def _IsClosedToNodeInGrid(self, x, y, z, level, grid, searchRadius, closestCoordinates):
        """
        检查当前节点是否靠近给定网格中的节点,是否有邻居节点
        :param x:
        :param y:
        :param z:
        :param level:
        :param grid:
        :param searchRadius:搜索半径
        :param closestCoordinates:找到的最近的点
        :return:找到则返回True
        """
        # L是邻居节点的相对位置列表，V是
        L = []
        V = []
        self._circular_search(x, y, z, grid, 1, searchRadius, L, V)
        found_closest = True if len(L) > 0 else False
        if found_closest:
            closestCoordinates.setXIndex(x + L[0].getXIndex())
            closestCoordinates.setYIndex(y + L[0].getYIndex())
            closestCoordinates.setZIndex(z + L[0].getZIndex())
        return found_closest

    def _circular_search(self, sg_idx_x, sg_idx_y, sg_idx_z, grid, max_neighbours_limit, max_radius_limit, l, v):
        """

        :param sg_idx_y:
        :param sg_idx_z:
        :param grid: _hdg
        :param max_neighbours_limit:
        :param max_radius_limit:
        :param l:
        :param v:
        :return:
        """
        found_cnt = [0]
        idx_x = idx_y = idx_z = 0
        max_x_offset = self._sg_dim_x - 1
        max_y_offset = self._sg_dim_y - 1
        max_z_offset = self._sg_dim_z - 1
        max_dim = max(max_x_offset, max_y_offset, max_z_offset)

        # 判断：如果_hdg在sg对应位置不是nan，那么就不用发生重定位
        if not is_nan(grid[sg_idx_z][sg_idx_y][sg_idx_x]):
            # 邻居节点计数+1，l加入相对位置（0，0，0），v加入硬数据值
            found_cnt[0] = found_cnt[0] + 1
            a_coords = Coords(0, 0, 0)
            l.append(Coords(a_coords.getXIndex(), a_coords.getYIndex(), a_coords.getZIndex()))
            v.append(grid[sg_idx_z][sg_idx_y][sg_idx_x])

        # i是偏移量：从1->max_dim循环
        for i in range(1, max_dim):

            # 判断：如果已经找到最大邻居节点限制的值，跳出循环
            if found_cnt[0] > max_neighbours_limit:
                break

            # 判断:如果偏移量大于领域半径，跳出循环
            if i > max_radius_limit != -1:
                break

            # 初始化三方向的具体偏移量
            x_offset = y_offset = z_offset = i
            # 初始化随机方向
            random_direction = random.randint(0, 0)

            #
            if random_direction == 0:
                # print(0)
                # direction + X
                idx_x = sg_idx_x + x_offset
                idx_x, idx_y, idx_z = self.search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt,
                                                                    max_neighbours_limit, x_offset, y_offset,
                                                                    z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v
                                                                    )
                # direction - X
                idx_x = sg_idx_x - x_offset
                idx_x, idx_y, idx_z = self.search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt,
                                                                    max_neighbours_limit, x_offset, y_offset,
                                                                    z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v
                                                                    )
                # direction + Y
                idx_y = sg_idx_y + y_offset
                idx_x, idx_y, idx_z = self.search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt,
                                                                    max_neighbours_limit, x_offset, y_offset,
                                                                    z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v
                                                                    )
                # direction - Y
                idx_y = sg_idx_y - y_offset
                idx_x, idx_y, idx_z = self.search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt,
                                                                    max_neighbours_limit, x_offset, y_offset,
                                                                    z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v
                                                                    )
                # direction +Z
                idx_z = sg_idx_z + z_offset
                idx_x, idx_y, idx_z = self.search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt,
                                                                    max_neighbours_limit, x_offset, y_offset,
                                                                    z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v
                                                                    )
                # direction -Z
                idx_z = sg_idx_z - z_offset
                idx_x, idx_y, idx_z = self.search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt,
                                                                    max_neighbours_limit, x_offset, y_offset,
                                                                    z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v
                                                                    )

    def search_data_in_direction(self, grid, direction, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,
                                 y_offset, z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v):
        """

        :param grid:
        :param direction:
        :param idx_x:
        :param idx_y:
        :param idx_z:
        :param found_cnt:
        :param max_neighbours_limit:
        :param x_offset:
        :param y_offset:
        :param z_offset:
        :param sg_idx_x:
        :param sg_idx_y:
        :param sg_idx_z:
        :param l:
        :param v:
        :return:
        """
        if direction == 0:  # Direction X
            for k in range(-y_offset, y_offset + 1):
                idx_y = sg_idx_y + k
                for j in range(-z_offset, z_offset + 1):
                    idx_z = sg_idx_z + j
                    # Adding value inside viewport only
                    if ((idx_x >= 0 and idx_x < self._sg_dim_x) and (idx_y >= 0 and idx_y < self._sg_dim_y) and (
                            idx_z >= 0 and idx_z < self._sg_dim_z)):
                        flag = self.adding_data(grid, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, sg_idx_x,
                                                sg_idx_y, sg_idx_z, l, v)
                        if flag == True:
                            return idx_x, idx_y, idx_z
            return idx_x, idx_y, idx_z
        elif direction == 1:  # Direction Y
            for k in range(-x_offset + 1, x_offset):
                idx_x = sg_idx_x + k
                for j in range(-z_offset + 1, z_offset):
                    idx_z = sg_idx_z + j
                    # Adding value inside viewport only
                    if ((idx_x >= 0 and idx_x < self._sg_dim_x) and (idx_y >= 0 and idx_y < self._sg_dim_y) and (
                            idx_z >= 0 and idx_z < self._sg_dim_z)):
                        flag = self.adding_data(grid, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, sg_idx_x,
                                                sg_idx_y, sg_idx_z, l, v)
                        if flag == True:
                            return idx_x, idx_y, idx_z
            return idx_x, idx_y, idx_z
        elif direction == 2:  # Direction Z
            for k in range(-x_offset + 1, x_offset):
                idx_x = sg_idx_x + k
                for j in range(-y_offset + 1, y_offset):
                    idx_y = sg_idx_y + j
                    # Adding value inside viewport only
                    if ((idx_x >= 0 and idx_x < self._sg_dim_x) and (idx_y >= 0 and idx_y < self._sg_dim_y) and (
                            idx_z >= 0 and idx_z < self._sg_dim_z)):
                        flag = self.adding_data(grid, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, sg_idx_x,
                                                sg_idx_y, sg_idx_z, l, v)
                        if flag == True:
                            return idx_x, idx_y, idx_z
            return idx_x, idx_y, idx_z

    def adding_data(self, grid, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, sg_idx_x, sg_idx_y, sg_idx_z, l, v):
        """

        :param idx_x:
        :param idx_y:
        :param idx_z:
        :param found_cnt:
        :param max_neighbours_limit:
        :param sg_idx_x:
        :param sg_idx_y:
        :param sg_idx_z:
        :param l:
        :param v:
        :return:
        """
        if not is_nan(grid[idx_z][idx_y][idx_x]):
            found_cnt[0] = found_cnt[0] + 1
            if found_cnt[0] > max_neighbours_limit:
                return True
            a_coords = Coords(0, 0, 0)
            a_coords.setXIndex(idx_x - sg_idx_x)
            a_coords.setYIndex(idx_y - sg_idx_y)
            a_coords.setZIndex(idx_z - sg_idx_z)
            for i in range(len(l)):
                if (a_coords.getXIndex(), a_coords.getYIndex(), a_coords.getZIndex()) == (l[i].getXIndex(), l[i].getYIndex(), l[i].getZIndex()):
                    # if (a_coords.get_x(), a_coords.get_y(), a_coords.get_z()) in l:
                    return False
            l.append(a_coords)
            v.append(grid[idx_z][idx_y][idx_x])
        return False

    def startSimulation(self):
        """
        开始模拟
        :return:
        """
        print("5:开始模拟")
        if self._debug_mode > -2:
            print("__________________________________________________________________________________")
            print("pyMPSLib: a python library for multiple point simulation")
            print("__________________________________________________________________________________")
        # 是否初始化随机种子:0则自动生成随机种子，非0则自己指定
        if self._seed != 0:
            random.seed(self._seed)

        # 获取输出文件名
        def find_last(search, target):
            """
            找到某字符串中指定字符最后出现的位置
            :param search: 需要搜索的字符串
            :param target: 用来搜索的字符
            :return: 该字符串中最后出现指定字符的位置，没有则返回-1
            """
            # 找到第一个字符所在位置
            pos = search.find(target)
            # 继续找
            while pos >= 0:
                # 从之前找到的位置 + 1开始找
                next_pos = search.find(target, pos + 1)
                if next_pos == -1:
                    # 没找到就直接返回
                    break
                pos = next_pos
            return pos

        # 用/和\分别匹配路径，谁在后面就用谁
        found1 = find_last(self._ti_filename, "/")
        found2 = find_last(self._ti_filename, "\\")
        found = found1 if found1 > found2 else found2
        output_filename = self._output_directory + "/" + self._ti_filename[found + 1:]
        print("6:filename：{}".format(output_filename))

        # 开始模拟
        total_seconds = 0
        last_progress = 0
        allocated_nodes_from_harddata = []
        node_to_putback = []
        # node_cnt = 0
        # total_nodes = 0

        self._sg_iterations = np.full([self._sg_dim_z, self._sg_dim_y, self._sg_dim_x], -1, dtype=float)
        self._sg = np.full([self._sg_dim_z, self._sg_dim_y, self._sg_dim_x], -1, dtype=float)

        for i in range(0, self._realization_numbers):
            # 记录开始模拟的时间
            begin_realization = process_time()
            print("7:start simulation time：{}".format(begin_realization))

            self._initializeSG(self._sg_iterations, self._sg_dim_x, self._sg_dim_y, self._sg_dim_z, 0)
            self._initializeSG(self._sg, self._sg_dim_x, self._sg_dim_y, self._sg_dim_z)
            #
            # if self._debug_mode > 1:
            #     self._initializeSG(self._tg1, self._sg_dim_x, self._sg_dim_y, self._sg_dim_z, 0)
            #     self._initializeSG(self._tg2, self._sg_dim_x, self._sg_dim_y, self._sg_dim_z, 0)
            print("init MG:{}".format(self._sg))

            """==============================================================================================
            改一下，待会改回去
            =============================================================================================="""
            # for z in range(0, self._sg_dim_z):
            #     for y in range(0, self._sg_dim_y):
            #         for x in range(0, self._sg_dim_x):
            #             if self._hdg.size != 0 and is_nan(self._sg[z][y][x]):
            #                 self._sg[z][y][x] = self._hdg[z][y][x]


            # 多层网格
            # 多层网格处于外层循环，因此搜索树的构建以及模拟网格点的模拟都是每个网格单独做的
            for level in range(self._total_grids_level, -1, -1):
                print("9:into muti-grid{}".format(level))
                self._InitStartSimulationEachMultipleGrid(level)

                # 对于从粗到细的每个空间级别
                offset = int(pow(2, level))  # 8-> 4 -> 2 -> 1

                # 为每个级别SG定义模拟路径
                if self._debug_mode > -1:
                    print("Define simulation path for each level ")
                self._simulation_path.clear()

                node_cnt = 0
                # **这一句之后看一下
                total_nodes = int(self._sg_dim_x / offset) * int(self._sg_dim_y / offset) * int(
                    self._sg_dim_z / offset)  # 0 -> 0 -> 0 ->6400
                # print(self._sg_dim_x, total_nodes)
                # print(self._ti_filename)
                # print(self._hardData_filenames)
                # print(self._hdg[0][57][3])

                # 模拟网格写入条件点数据
                for z in range(0, self._sg_dim_z, offset):
                    for y in range(0, self._sg_dim_y, offset):
                        for x in range(0, self._sg_dim_x, offset):
                            sg_1D_idx = threeD_to_1D(x, y, z, self._sg_dim_x, self._sg_dim_y)
                            self._simulation_path.append(sg_1D_idx)

                            """==============================================================================================
                            =============================================================================================="""
                            if level != 0:
                                self._fillSGfromHD(x, y, z, level, allocated_nodes_from_harddata, node_to_putback)
                            elif level == 0 and len(self._hdg) != 0 and is_nan(self._sg[z][y][x]):
                                self._sg[z][y][x] = self._hdg[z][y][x]






                if self._debug_mode > 2:
                    output_filepath = output_filename + ".gslib"
                    write_sgems_file(output_filepath, self._sg, self._sg_dim_z, self._sg_dim_y, self._sg_dim_x)
                    self._showSG()

                # Shuffle simulation path indices vector for a random path
                if self._debug_mode > -1:
                    print("Shuffling simulation path using type {}".format(self._shuffle_sg_path))
                #
                # 如果没有软数据则返回随机路径
                if len(self._softData_grids) == 0 and self._shuffle_sg_path == 2:
                    print("WARNING: no soft data found, switch to random path")
                    self._shuffle_sg_path = 1
                #
                # 打乱
                if self._shuffle_sg_path == 1:
                    # 随机打乱
                    # print(self._simulation_path)
                    random.shuffle(self._simulation_path)
                    # print("打乱之后的模拟顺序为{}".format(self._simulation_path))
                else:
                    # shuffling preferential to soft data
                    # **待实现
                    self._shuffleSgPathPreferentialToSoftData(level)

                # 执行模拟
                # 对路径中的每个值
                progression_cnt = 0
                total_nodes = int(len(self._simulation_path))

                if self._debug_mode > 1:
                    print("17:start sequential simulation")

                # # 从SG清除分配的数据
                # # _clearSGFromHD(allocatedNodesFromHardData);

                # ---------------------------------------
                # 这里将类变量赋值给局部变量
                # simulation_path = self._simulation_path
                # sg_dim_x = self._sg_dim_x
                # sg_dim_y = self._sg_dim_y
                # sg = self._sg

                for ii in range(0, len(self._simulation_path)):
                    # 最内层循环，对多层模拟网格中已经定好模拟路径的每个点进行模拟
                    # 每个点都有对应的数据样板，然后找出搜索树中对应的数据样板，会得出一个字典{x=0: a ,x=1: b }（x指待模拟点是0或1的次数）,然后通过这个概率随机抽一个作为模拟结果
                    # for ii in range(0, len(simulation_path)):

                    # 获取结点坐标
                    SG_idx_z, SG_idx_y, SG_idx_x = oneD_to_3D(self._simulation_path[ii], self._sg_dim_x, self._sg_dim_y)
                    # SG_idx_z, SG_idx_y, SG_idx_x = oneD_to_3D(simulation_path[ii], sg_dim_x, sg_dim_y)

                    # print(SG_idx_z, SG_idx_y, SG_idx_x)
                    # print(self._sg)
                    # print(self._sg[SG_idx_z][SG_idx_y][SG_idx_x])

                    # 执行模拟直到没有 NaN 值...
                    if is_nan(self._sg[SG_idx_z][SG_idx_y][SG_idx_x]):
                        self._sg[SG_idx_z][SG_idx_y][SG_idx_x] = self._simulate(SG_idx_x, SG_idx_y, SG_idx_z, level)
                    # if is_nan(sg[SG_idx_z][SG_idx_y][SG_idx_x]):
                    #     sg[SG_idx_z][SG_idx_y][SG_idx_x] = self._simulate(SG_idx_x, SG_idx_y, SG_idx_z, level)

                    # 计算模拟阶段
                    if self._debug_mode > -1:
                        progress = int(progression_cnt / float(total_nodes) * 100)
                        progression_cnt = progression_cnt + 1
                        if progress % 5 == 0 and progress != last_progress:
                            last_progress = progress
                            end_node = process_time()
                            # print(":结束模拟时间：{}".format(end_node))
                            elapse_node_secs = float(end_node - begin_realization)
                            # print(begin_realization,end_node)
                            node_estimated_secs = int(
                                (elapse_node_secs / float(progression_cnt)) * float(total_nodes - progression_cnt))
                            # print(node_estimated_secs)
                            hours, minutes, seconds = secondsToHrMnSec(node_estimated_secs)
                            if progress > 0:
                                print("Level:{} Progression (%):{} finish in {}hours {}minutes {}seconds".format(level,
                                                                                                                 progress,
                                                                                                                 hours,
                                                                                                                 minutes,
                                                                                                                 seconds))


                # debug
                if self._debug_mode > 2:
                    print(output_filename)
                    # write_sgems_file(output_filename)
                """==============================================================================================
                =============================================================================================="""
                if level != 0:
                    self._clearSGFromHD(allocated_nodes_from_harddata, node_to_putback)
                if self._debug_mode > 2:
                    pass
                if self._debug_mode > 2:
                    pass
                print("-----------------------------------")

            # 画图
            if self._debug_mode > 0:
                self._showSG()

            # 计算该层网格耗时
            if self._debug_mode > -1:
                end_realization = process_time()
                print(end_realization)
                elapsed_realization_secs = float(end_realization - begin_realization)
                total_seconds = total_seconds + elapsed_realization_secs
                print("Elapsed time (sec): {}         total:{}".format(elapsed_realization_secs, total_seconds))

            # 写入结果
            if self._debug_mode > -2:
                # 将结果写入文件
                if self._debug_mode > -1:
                    print("Persisting....")
                write_sgems_file(output_filename + "snesim" + "sg" + str(i) + ".gslib", self._sg, self._sg_dim_z, self._sg_dim_y,
                                 self._sg_dim_x)

        # 计算总耗时
        if self._debug_mode > -1:
            hours, minutes, seconds = secondsToHrMnSec(int(total_seconds / self._realization_numbers))
            print("Total simulation time {}s".format(total_seconds))
            print(
                "Average time for {}  simulations (hours:minutes:seconds) : {}:{}:{}".format(self._realization_numbers,
                                                                                             hours, minutes, seconds))

        # # ETYPE
        # Etype.DrawEtype(self._output_directory)
        #
        # # MDS
        # MDS.DrawMDS()


        # 打印信息
        if self._debug_mode > -1:
            print("Number of threads: {}".format(self._number_of_threads))
            print("Conditional points: {}".format(self._max_neighbours))
            print("Max iterations: {}".format(self._max_iterations))
            print("SG: {} {} {}".format(self._sg_dim_x, self._sg_dim_y, self._sg_dim_z))
            print("TI: {} {} {} {}".format(self._ti_filename, self._ti_dim_x, self._ti_dim_y, self._ti_dim_z))

    def _initializeSG(self, sg, sg_dim_x, sg_dim_y, sg_dim_z, value=np.nan):
        """
        初始化模拟网格
        :param sg:模拟网格
        :param sg_dim_x:self._sg_dim_x
        :param sg_dim_y:self._sg_dim_y
        :param sg_dim_z:self._sg_dim_z
        :param value:默认为nan
        :return:
        """
        print("8：initing SG")
        for z in range(0, sg_dim_z):
            for y in range(0, sg_dim_y):
                for x in range(0, sg_dim_x):
                    sg[z][y][x] = value

    def _initilizePath(self, sg_dim_x, sg_dim_y, sg_dim_z, path):
        """
        初始化序列模拟路径
        :param sg_dim_x:模拟网格x维大小
        :param sg_dim_y:模拟网格y维大小
        :param sg_dim_z:模拟网格z维大小
        :param path:序列模拟路径
        :return:
        """
        # Putting sequential indices
        cnt = 0
        for z in range(0, sg_dim_z):
            for y in range(0, sg_dim_y):
                for x in range(0, sg_dim_x):
                    path.append(cnt)
                    cnt = cnt + 1
        print("13:simulation path：{}".format(path))

    def _showSG(self):
        pass
