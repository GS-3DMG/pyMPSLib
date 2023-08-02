def is_nan(x):
    """
    判断一个数是否为nan，nan不能直接==比较，但是nan!=nan
    :param x:一个数
    :return:是否是nan
    """
    if x != x:
        return True
    else:
        return False


def oneD_to_3D(oneD_index, dim_x, dim_y):
    """
    将1D的目录转换为3D的坐标
    :param oneD_index: 1D的目录
    :param dim_x: 3D坐标x维大小
    :param dim_y: 3D坐标y维大小
    :return:3D坐标x,y,z
    """
    idx_z = int(oneD_index / (dim_x * dim_y))
    idx_y = int((oneD_index - idx_z * dim_x * dim_y) / dim_x)
    idx_x = int(oneD_index - dim_x * (idx_y + dim_y * idx_z))
    return idx_z, idx_y, idx_x


def threeD_to_1D(idx_x, idx_y, idx_z, dim_x, dim_y):
    """
    将3D的坐标转换为1D的目录
    :param idx_x: 3D坐标x的坐标
    :param idx_y: 3D坐标y的坐标
    :param idx_z: 3D坐标z的坐标
    :param dim_x: 3D坐标x维大小
    :param dim_y: 3D坐标y维大小
    :return:1D目录
    """
    oneD_index = idx_x + dim_x * (idx_y + idx_z * dim_y)
    return oneD_index


def secondsToHrMnSec(seconds):
    """
    将秒数转换为时分秒格式
    :param seconds:秒数
    :return:时、分、秒
    """
    minute = int(seconds / 60)
    second = int(seconds % 60)
    hour = int(minute / 60)
    minute = int(minute % 60)
    return hour, minute, second
