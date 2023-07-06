import sys
import numpy as np
import os


def read_sgems_file(path):
    """
    读取sgems格式的训练图像文件
    :param path: 文件路径
    :return: np.array数组
    """
    file = open(path)
    line = file.readline()
    line = line.replace("\n", "")
    line = line.replace("\t", " ")
    x_scale, y_scale, z_scale = line.split(" ")
    x_scale_int, y_scale_int, z_scale_int = int(x_scale), int(y_scale), int(z_scale)
    _TI = np.full([z_scale_int, y_scale_int, x_scale_int], -1)
    cat = file.readline()
    var = file.readline()
    value_list = []
    while 1:
        line = file.readline()
        if not line:
            break
        line = line.replace("\n", "")
        value_list.append(float(line))
    file.close()
    cnt = 0
    for z in range(0, z_scale_int):
        for y in range(0, y_scale_int):
            for x in range(0, x_scale_int):
                _TI[z][y][x] = value_list[cnt]
                cnt = cnt + 1
    return _TI


def read_con_sgems_file(path):
    """
    读取sgems格式的条件数据文件
    :param path: 文件路径
    :return: np.array数组
    """
    file = open(path)
    param_list = []
    cnt = 0
    while 1:
        line = file.readline()
        if not line:
            break
        cnt = cnt + 1
        if cnt < 7:
            continue
        line = line.replace("\n", "")
        arr = ' '.join(line.split())
        # arr = line.split(" ")
        param_list.append(arr)
    file.close()
    return np.array(param_list)

def read_soft_con_sgems_file(path, categories, x, y, z):
    """
    write soft data file to soft grids
    :param path: soft data path
    :param categories: categories of soft data
    :param x
    :param y
    :param z
    :return:
    """
    file = open(path)
    param_list = []
    cnt = 0
    while 1:
        line = file.readline()
        if not line:
            break
        cnt = cnt + 1
        if cnt <= 5 + categories:
            continue
        line = line.replace("\n", "")
        arr = ' '.join(line.split())
        # arr = line.split(" ")
        param_list.append(arr)
    soft_list = [float(y) for x in param_list for y in x.split(" ")]
    soft_arrays = np.full((categories,z,y,x),np.nan)
    for i in range(categories):
        soft_list_i = []
        for j in range(x*y):
            soft_list_i.append(soft_list[(3+i)+(5*j)])
        soft_array = np.array(soft_list_i).reshape(y,x)
        soft_arrays[i,:,:,:]= soft_array
        pass
    # soft_array = np.array(soft_list).reshape(z* categories,x,y)
    file.close()
    return soft_arrays


def write_con_sgems_file(path, data_list):
    """
    写条件数据到文件
    :param path: 写入路径
    :param data_list: 条件数据列表，list item为 x y z value
    :return:
    """
    with open(path, 'w') as file:
        file.write(str(len(data_list)) + "\n4\nx\ny\nz\nsample\n")
        for i in range(0, len(data_list)):
            file.write(str(data_list[i]) + "\n")
    pass


def write_sgems_file(path, _SG, z_size, y_size, x_size):
    """
    写网格数据到文件
    :param path: 写入路径
    :param _SG: 模拟网格
    :param z_size: z 大小
    :param y_size: y 大小
    :param x_size: x 大小
    :return:
    """
    with open(path, 'w') as file:
        file.write(
            str(x_size) + " " + str(y_size) + " " + str(z_size) + "\n1\nv")
        for z in range(0, z_size):
            for y in range(0, y_size):
                for x in range(0, x_size):
                    file.write("\n" + str(_SG[z][y][x]))

    pass


def read_line_configuration(path, data_list):
    """

    :param path:
    :param data_list:
    :return:
    """
    print("4:开始读每一行文件")
    file = open(path, 'r')
    line = file.readline().replace(" ", "").rstrip('\n')  # q去除空格
    while line:
        for word in line.split('#'):
            data_list.append(word)
        line = file.readline().replace(" ", "").rstrip('\n')

def readConfigurations(file_name):
    """

    :param filename:
    :return:
    """
    print("---------------开始读取配置文件--------")
    # 检查文件是否存在
    if not (os.path.isfile(file_name)):
        print("Paremeter file {} does not exist --> quitting".format(file_name))
        exit(0)
    data = []
    read_line_configuration(file_name, data)
    print(data)
    return data
