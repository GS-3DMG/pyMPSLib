import functools
import os
from math import floor
from random import random
import numpy as np
from .Coords import Coords
from .MPSAlgorithm import MPSAlgorithm
from ..utils.FileUtil import read_line_configuration
from ..utils.utility import oneD_to_3D


class SNESIM(MPSAlgorithm):
    class TemplateSorter:
        def __init__(self, _template_size_x, _template_size_y, _template_size_z):
            """
            模板排序类的构造函数
            :param _template_size_x:模板点的x坐标
            :param _template_size_y:模板点的y坐标
            :param _template_size_z:模板点的z坐标
            """
            self._template_size_x = _template_size_x
            self._template_size_y = _template_size_y
            self._template_size_z = _template_size_z

        def __call__(self, idx1, idx2):
            """
            使TemplateSorter类变成一个可调用类,提供数据模板遍历的排序方法
            :param idx1:模板点1
            :param idx2:模板点2
            :return:若模板点1离中心点的距离<=模板点2离中心点的距离则返回-1
            """
            # 找出中心点
            template_center_x = int(floor(self._template_size_x / 2))
            template_center_y = int(floor(self._template_size_y / 2))
            template_center_z = int(floor(self._template_size_z / 2))
            # 把数值点转化为三维坐标
            idx1_z, idx1_y, idx1_x = oneD_to_3D(idx1, self._template_size_x, self._template_size_y)
            idx2_z, idx2_y, idx2_x = oneD_to_3D(idx2, self._template_size_x, self._template_size_y)
            # 计算两个比较的点和中心点三维坐标的距离
            idx1_total_distance = pow(idx1_x - template_center_x, 2) + pow(idx1_y - template_center_y, 2) + pow(idx1_z - template_center_z,2)
            idx2_total_distance = pow(idx2_x - template_center_x, 2) + pow(idx2_y - template_center_y, 2) + pow(idx2_z - template_center_z, 2)
            # 小于就是负数，不换位置，
            if idx1_total_distance < idx2_total_distance:
                return -1
            elif idx1_total_distance > idx2_total_distance:
                return 1
            else:
                return 0

    def __init__(self):
        """
        SNESIM类的构造函数，继承了MAPSAlgorithm类的实例变量
        """
        super().__init__()
        self._template_size_x = 0
        self._template_size_y = 0
        self._template_size_z = 0
        self._min_node_count = 0
        self._template_faces = []

    def _readConfigurations(self, file_name):
        """
        读取配置文件mps_snesim.txt
        :param file_name: 配置文件名mps_snesim.txt
        :return:
        """
        print("3:开始读配置文件")
        # 检查文件是否存在
        if not (os.path.isfile(file_name)):
            print("Paremeter file {} does not exist --> quitting".format(file_name))
            exit(0)
        # 读取文件里的每一行数据
        data = []
        read_line_configuration(file_name, data)
        print(data)
        self._realization_numbers = int(data[1])
        self._seed = float(data[3])
        self._total_grids_level = int(data[5])
        self._min_node_count = int(data[7])
        self._max_cond_data = int(data[9])
        self._template_size_x = int(data[11])
        self._template_size_y = int(data[13])
        self._template_size_z = int(data[15])
        self._sg_dim_x = int(data[17])
        self._sg_dim_y = int(data[19])
        self._sg_dim_z = int(data[21])
        self._sg_world_min_x = int(data[23])
        self._sg_world_min_y = int(data[25])
        self._sg_world_min_z = int(data[27])
        self._sg_cell_size_x = int(data[29])
        self._sg_cell_size_y = int(data[31])
        self._sg_cell_size_z = int(data[33])
        # TI filename
        self._ti_filename = data[35]
        self._output_directory = data[37]
        self._shuffle_sg_path = int(data[39])
        print(self._shuffle_sg_path)
        self._shuffle_entropy_factor = 4
        print(data[43])
        self._shuffle_ti_path = (int(data[41]) != 0)
        self._hardData_filenames = data[43]
        self._hd_search_radius = float(data[45])
        self._hd_search_radius = max(self._template_size_x, self._template_size_y, self._template_size_z)
        # 后面的软数据先不写
        for i in data[47].split(';'):
            self._softData_categories.append(float(i))
        self._softData_filenames = data[49]
        print(self._softData_categories, self._softData_filenames)
        # 把grid resize成网格数量这么长，可能是存放两个网格？但是list本来就可变就不写了
        self._number_of_threads = int(data[51])
        self._debug_mode = int(data[53])

    def _constructTemplateFaces(self, size_x, size_y, size_z):
        """
        构造模板板面(每个点相对于模板中心的位置)并围绕模板中心对它们进行排序
        :param size_x: template_x:数据模板的x维大小
        :param size_y: template_y:数据模板的y维大小
        :param size_z: template_z:数据模板的z维大小
        :return:
        """
        print("12:start construct template")
        template_center_x = int(floor(size_x / 2))
        template_center_y = int(floor(size_y / 2))
        template_center_z = int(floor(size_z / 2))
        print("Template center x:{} y:{} z:{}".format(template_center_x, template_center_y, template_center_z))
        total_template_indices = size_x * size_y * size_z  # 模板总共有多少个数
        total_templates = 0
        # 创建模板路径
        template_path = []
        self._initilizePath(size_x, size_y, size_z, template_path)
        # 用每个点与中心的距离对模板路径排序
        templateSorter = self.TemplateSorter(size_x, size_y, size_z)
        # print(templatSorter(template_path[2], template_path[3]))
        template_path.sort(key=functools.cmp_to_key(templateSorter))
        print("14:Actual simulation path：{}".format(template_path))
        # 循环通过所有的模板指数
        # 初始化faces
        self._template_faces.clear()
        self._template_faces.append(Coords(0, 0, 0, 0))
        print("15:")
        for i in range(0, total_template_indices):
            template_idx_z, template_idx_y, template_idx_x = oneD_to_3D(template_path[i], size_x, size_y)
            offset_x = template_idx_x - template_center_x
            offset_y = template_idx_y - template_center_y
            offset_z = template_idx_z - template_center_z
            if offset_x != 0 or offset_y != 0 or offset_z != 0:
                self._template_faces.append(Coords(offset_x, offset_y, offset_z, 0))
            print("The position of the point {} relative to the center of the simulated grid is {}".format(i + 1, self._template_faces[i].coords2String()))

    def _cpdf(self, condition_points, x, y, z):
        """
        条件概率分布函数
        :param condition_points:条件点的字典例如{0:30, 1:70}
        :param x:软数据使用
        :param y:软数据使用
        :param z:软数据使用
        :return:通过条件概率分布，随机取一个值
        """
        found_value = np.nan
        total_counter = 0
        for value in condition_points:
            total_counter += condition_points[value]
        probabilities_from_TI = {}
        for value in condition_points:
            probabilities_from_TI[value] = float(condition_points[value] / float(total_counter))
        probabilities_combined = {}

        # 软数据先不写
        use_soft_data = True
        if len(self._softData_grids) == 0:
            use_soft_data = False
        # 0没有那1也没有
        elif np.isnan(self._softData_grids[0][z][y][x]):
            use_soft_data = False

        if use_soft_data:
            probabilities_from_softData = {}
            sum_probability = 0
            last_index = len(self._softData_categories) - 1
            for i in range(last_index):
                sum_probability += self._softData_grids[i][z][y][x]
                probabilities_from_softData[self._softData_categories[i]] = self._softData_grids[i][z][y][x]
            # 最后一种类别直接做减法获取
            probabilities_from_softData[self._softData_categories[last_index]] = 1 - sum_probability

            # 计算TI-Soft data联合概率分布
            total_value = 0
            for value in probabilities_from_softData:
                if value in probabilities_from_TI:
                    total_value += probabilities_from_softData[value] * probabilities_from_TI[value]
                else:
                    total_value += 0

            cumulate_value = 0
            for value in probabilities_from_softData:
                if value in probabilities_from_TI:
                    cumulate_value += (probabilities_from_softData[value] * probabilities_from_TI[value]) / total_value
                else:
                    cumulate_value += 0
                probabilities_combined[cumulate_value] = value
                if cumulate_value == 1.0:
                    break
        else:
            cumulate_value = 0
            for value in probabilities_from_TI:
                # print(value, probabilities_from_TI[value])
                cumulate_value += probabilities_from_TI[value]
                probabilities_combined[cumulate_value] = value
                # {0:0.73, 1:1}->[0,0.73]  [0.73,1]
        # 产生一个[0,1)的随机数
        random_value = random()
        # 落在哪个区域内就把found_value设定成对应的value值
        for iter in probabilities_combined:
            if iter >= random_value:
                found_value = probabilities_combined[iter]
                break
        return found_value
