import os
from math import ceil
import numpy as np
from .SNESIM import SNESIM
from ..utils import FileUtil
from ..utils.utility import is_nan


class SNESIMTree(SNESIM):
    class TreeNode:
        def __init__(self):
            """
            初始化一个数结点
            """

            self.value = 0.0
            self.counter = 0
            self.level = 0
            self.children = []

    def __init__(self, configuration_file):
        """
        SNESIMTree类的构造函数
        :param configuration_file:配置文件
        :return:
        """
        super().__init__()
        self.initialize(configuration_file)
        self._search_tree = []  # 里面存的是TreeNode对象
        self._min_node_count = 0

    def initialize(self, configuration_file):
        """
        初始化
        :param configuration_file: "mps_snesim.txt"
        :return:
        """
        # 读配置文件
        print("2:initing....")
        super()._readConfigurations(configuration_file)
        # 读训练图像的np数组
        self._TI = FileUtil.read_sgems_file(self._ti_filename)
        # 读软数据文件
        if os.path.exists(self._softData_filenames):
            self._softData_grids = FileUtil.read_soft_con_sgems_file(self._softData_filenames, len(self._softData_categories), self._sg_dim_x, self._sg_dim_y, self._sg_dim_z)

        # 读硬数据文件
        if os.path.exists(self._hardData_filenames):
            a = FileUtil.read_con_sgems_file(self._hardData_filenames)
            # print(a)
            hd_list = [int(float(y)) for x in a for y in x.split(" ")]
            # print(hd_list)
            print(self._sg_dim_z, self._sg_dim_y, self._sg_dim_x)
            self._hdg = np.full([self._sg_dim_z, self._sg_dim_y, self._sg_dim_x], -1, dtype=float)
            # print(self._hdg.size)
            for z in range(0, self._sg_dim_z):
                for y in range(0, self._sg_dim_y):
                    for x in range(0, self._sg_dim_x):
                        self._hdg[z][y][x] = np.nan
            # print(self._hdg)
            # print(len(hd_list))
            for i in range(0, len(hd_list), 4):
                print(i, i+1, i+2, i+3)
                points = hd_list[i:i + 4]
                # print(points)
                #
                # print(points[i % 4+2], points[i % 4], points[i % 4+1], points[i % 4+3])

                # conditional.dat
                # self._hdg[points[i % 4 + 2]][points[i % 4 + 1]][points[i % 4]] = points[i % 4 + 3]
                # sgems
                self._hdg[points[i % 4 + 2] - 1][points[i % 4 + 1] - 1][points[i % 4] - 1] = points[i % 4 + 3]
        # print(self._hdg[0][57][3])
        # 维度确认
        self._ti_dim_z = self._TI.shape[0]
        self._ti_dim_y = self._TI.shape[1]
        self._ti_dim_x = self._TI.shape[2]
        # print(self._ti_dim_z, self._ti_dim_y, self._ti_dim_x)

    def startsimulation(self):
        """
        开始模拟
        :return:
        """
        super().startsimulation()

    def _simulate(self, sg_idx_x, sg_idx_y, sg_idx_z, level):
        """
        对sg中的每个点进行模拟
        :param sg_idx_x:待模拟点的x坐标
        :param sg_idx_y:待模拟点的y坐标
        :param sg_idx_z:待模拟点的z坐标
        :param level:模拟网格的层数
        :return:模拟得出的值
        """
        # print("16：成功：进入senesim的每个点模拟过程")
        # 用结点的值初始化
        found_value = self._sg[sg_idx_z][sg_idx_y][sg_idx_x]
        # if sg_idx_x == 22 and sg_idx_y == 25:
        #     print(self._sg[sg_idx_z][sg_idx_y-8][sg_idx_x])
        # 如果是nan值的话就开始模拟
        # if is_nan(self._sg[sg_idx_z][sg_idx_y][sg_idx_x]):
        if is_nan(found_value):
            offset = pow(2, level)
            found_value = np.nan
            max_conditional_points = -1
            condition_points_used_cnt = 0
            a_partial_template = []
            # 遍历适用于【除模板中心的第一个点外】的所有可用模板集合

            # -----------------------------------------------改
            # template_faces = self._template_faces
            for i in range(1, len(self._template_faces)):
                # 通过offset扩展相对位置（0,-1,0）->(0,-8,0)
                delta_x = offset * self._template_faces[i].getXIndex()
                delta_y = offset * self._template_faces[i].getYIndex()
                delta_z = offset * self._template_faces[i].getZIndex()
            # for i in range(1, len(template_faces)):
            #     # 通过offset扩展相对位置（0,-1,0）->(0,-8,0)
            #     delta_x = offset * template_faces[i].getXIndex()
            #     delta_y = offset * template_faces[i].getYIndex()
            #     delta_z = offset * template_faces[i].getZIndex()

                # 将原有的位置加上相对位置，即是 该像素对应数据样板 在sg图像中的位置
                sg_x = sg_idx_x + delta_x
                sg_y = sg_idx_y + delta_y
                sg_z = sg_idx_z + delta_z
                # 如果sg中检查的模板点未越界，越界则在部分模板中加入nan值
                if not (sg_x < 0 or sg_x >= self._sg_dim_x) and not (sg_y < 0 or sg_y >= self._sg_dim_y) \
                        and not (sg_z < 0 or sg_z >= self._sg_dim_z):
                    # 如果sg中检查的对应位置模板点不是nan值(有条件数据或已经被模拟赋值过了),在部分模板中加入sg的原值，否则加入nan值
                    if not is_nan(self._sg[sg_z][sg_y][sg_x]):
                        a_partial_template.append(self._sg[sg_z][sg_y][sg_x])
                        # print(a_partial_template, sg_x, sg_y)
                    else:
                        a_partial_template.append(np.nan)
                # 如果越界则直接加入nan值
                else:
                    a_partial_template.append(np.nan)
            # print(len(a_partial_template))
            # 49-1 -> 36-1 -> 25-1 -> 16-1

            # 遍历搜索树并获取当前模板的值
            current_tree_node = []
            nodes_to_check = []
            conditional_points = {}
            sum_counter = 0
            current_level = 0
            max_level = 0

            # 遍历搜索树根结点（0/1）
            # print(self._search_tree[0],self._search_tree[1])
            for j in range(0, len(self._search_tree)):  # 搜索树根节点只有0或1
                # print(self._search_tree[j].value)
                condition_points_used_cnt = 0
                max_level = 0
                sum_counter = self._search_tree[j].counter
                # print(sum_counter)
                nodes_to_check.clear()
                nodes_to_check.append(self._search_tree[j].children)
                # 将level1的所有结点（0或1）加入到【待测结点】
                while len(nodes_to_check) > 0:
                    current_tree_node = nodes_to_check[-1]
                    nodes_to_check.pop()
                    for i in range(0, len(current_tree_node)):
                        if is_nan(a_partial_template[current_tree_node[i].level - 1]):
                            # 如果待比对模板点的值为nan，这个点与构建数据事件无关（只能通过已知点才能构建数据事件，从而查找搜索树），则继续查找下一层子树（实则是看下一个partial_template还是不是nan）
                            nodes_to_check.insert(0, current_tree_node[i].children)
                        elif current_tree_node[i].value == a_partial_template[current_tree_node[i].level - 1]:
                            # 如果该模板点匹配上了树结点，数据事件的范围得以缩小，记录下此时的level
                            current_level = current_tree_node[i].level
                            if current_level > max_level:
                                max_level = current_level
                                sum_counter = current_tree_node[i].counter
                                condition_points_used_cnt = condition_points_used_cnt + 1
                            elif current_level == max_level:
                                sum_counter = sum_counter + current_tree_node[i].counter

                            # 模板点匹配上了树结点，如果他的子节点counter仍不为0，那说明还有值，就继续向下搜索 ?1 and (?2 or 1) == ?1
                            if (current_tree_node[i].counter > self._min_node_count) and (
                                    condition_points_used_cnt < self._max_cond_data or self._max_cond_data == -1):
                                nodes_to_check.insert(0, current_tree_node[i].children)

                # print(self._search_tree[level][j].value+" "+sum_counter+" "+max_level)
                if condition_points_used_cnt > max_conditional_points:
                    # print(self._search_tree[j].value, sum_counter, condition_points_used_cnt)
                    conditional_points.clear()
                    conditional_points[self._search_tree[j].value] = sum_counter
                    max_conditional_points = condition_points_used_cnt
                elif condition_points_used_cnt == max_conditional_points:
                    conditional_points[self._search_tree[j].value] = sum_counter

            if self._debug_mode > 1:
                self._tg1[sg_idx_z][sg_idx_y][sg_idx_x] = condition_points_used_cnt

            found_value = self._cpdf(conditional_points, sg_idx_x, sg_idx_y, sg_idx_z)
        return found_value

    def _InitStartSimulationEachMultipleGrid(self, level):
        """
        初始化每一级多重网格
        :param level:当前的网格是第几级
        :return:
        """
        # 先这样写着
        print("10:initing MG")
        total_level = self._total_grids_level
        # print(total_level)

        # 自适应模板大小，供以后使用
        min_template_x = 4 if 4 < self._template_size_x else self._template_size_x
        min_template_y = 4 if 4 < self._template_size_y else self._template_size_y
        min_template_z = 4 if 4 < self._template_size_z else self._template_size_z

        template_x = min_template_x
        template_y = min_template_y
        template_z = min_template_z

        # 根据当前级别调整模板大小，级别越低模板越小 7->6->5->4
        template_x = int(self._template_size_x - (total_level - level) * (
                ceil(self._template_size_x - min_template_x) / total_level))
        template_y = int(self._template_size_y - (total_level - level) * (
                ceil(self._template_size_y - min_template_y) / total_level))
        template_z = int(self._template_size_z - (total_level - level) * (
                ceil(self._template_size_z - min_template_z) / total_level))

        print("11:size of template {} {} {}".format(template_x, template_y, template_z))
        # 构建模板结构
        # 例如3*3*1的模板
        # [0 1 2
        #  3 4 5
        #  6 7 8]
        # 先会得到一个先后遍历模板的顺序：从中间到两边[4 7 5 3 1 8 6 2 0],再将各点相对于中心点4的相对位置存入列表
        self._constructTemplateFaces(template_x, template_y, template_z)

        # 扫描训练图像，并构建搜索树
        # 构建搜索树
        self._search_tree.clear()
        # root = self.TreeNode()
        # self._search_tree.append(root)
        offset = pow(2, level)  # 2^level
        if self._debug_mode > -1:
            print("level:{} offset:{}".format(level, offset))
            print("original template size X:{},adjusted template size X:{}".format(self._template_size_x, template_x))
            print("original template size Y:{},adjusted template size Y:{}".format(self._template_size_y, template_y))
            print("original template size Z:{},adjusted template size Z:{}".format(self._template_size_z, template_z))

        node_cnt = 0
        found_existing_value = False
        found_idx = 0
        total_nodes = self._ti_dim_x * self._ti_dim_y * self._ti_dim_z
        last_progress = 0
        current_tree_node = self._search_tree

        # 对训练图像中所有的像素点进行遍历，根据他们的数据样板进行计数，构建搜索树
        # 数据样板是通过偏移量进行扩展之后的
        for z in range(0, self._ti_dim_z):
            for y in range(0, self._ti_dim_y):
                for x in range(0, self._ti_dim_x):
                    # print("网格中需要进行求值的点为({}, {}, {})".format(x, y, z))
                    # 遍历每个像素
                    node_cnt = node_cnt + 1
                    if self._debug_mode > -1:
                        progress = int(node_cnt / float(total_nodes) * 100)
                        if progress % 10 == 0 and progress != last_progress:
                            last_progress = progress
                            print("Building search tree at level:{} Progression (%):{}".format(level, progress))
                    current_tree_node = self._search_tree

                    # 找出该像素的 数据样板 的所有点
                    for i in range(0, len(self._template_faces)):
                        # 通过offset扩展相对位置（0,-1,0）->(0,-8,0)
                        delta_x = offset * self._template_faces[i].getXIndex()
                        delta_y = offset * self._template_faces[i].getYIndex()
                        delta_z = offset * self._template_faces[i].getZIndex()
                        # 将原有的位置加上相对位置，即是 该像素对应数据样板 在ti图像中的位置
                        ti_x = x + delta_x
                        ti_y = y + delta_y
                        ti_z = z + delta_z
                        # print("  他的数据样板的第{}个点的坐标为({}, {}, {})".format(i + 1, ti_x, ti_y, ti_z))

                        found_existing_value = False
                        found_idx = 0
                        # 检查nan值
                        # 处于训练图像边界的点往往数据模板很容易越界，会直接进行下一个点，因此可以加快运行效率
                        if (ti_x < 0 or ti_x >= self._ti_dim_x) or (ti_y < 0 or ti_y >= self._ti_dim_y) \
                                or (ti_z < 0 or ti_z >= self._ti_dim_z) or is_nan(self._TI[ti_z][ti_x][ti_y]):
                            # 注意和C++的vector不一样
                            # 当数据样板值在边界外的时候，直接将其舍弃掉
                            # print("  数据样板越界，直接进行SG中下一个点的匹配")
                            break
                        else:
                            # print(len(current_tree_node))
                            for j in range(0, len(current_tree_node)):
                                # print(self._TI[ti_z][ti_y][ti_x], current_tree_node[j].value)
                                if self._TI[ti_z][ti_y][ti_x] == current_tree_node[j].value:
                                    # print("  在搜索树上找到了该结构，计数加一")
                                    found_existing_value = True
                                    current_tree_node[j].counter = current_tree_node[j].counter + 1
                                    found_idx = j
                                    break

                            if not found_existing_value:
                                # print("  在搜索树上未找到该结构，将其加入搜索树")
                                a_treeNode = self.TreeNode()
                                a_treeNode.counter = 1
                                a_treeNode.value = self._TI[ti_z][ti_y][ti_x]
                                a_treeNode.level = i
                                current_tree_node.append(a_treeNode)
                                found_idx = int(len(current_tree_node) - 1)
                                # print(current_tree_node[found_idx].counter, current_tree_node[found_idx].value,
                                # current_tree_node[found_idx].level)
                            current_tree_node = current_tree_node[found_idx].children
        print(self._search_tree[0].counter, self._search_tree[1].counter)
        for i in range(0, len(self._search_tree[0].children)):
            print(self._search_tree[0].children[i].counter)
        if self._debug_mode > -1:
            print("Finish building search tree")

    def __del__(self):
        """
        析构函数
        :return:
        """
        pass
