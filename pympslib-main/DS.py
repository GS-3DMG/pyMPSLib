import random
import sys
import time
import numpy as np
from .utils import Etype

from .utils import FileUtil

def load_Samples(file_path):
    """
             加载训练图像文件
             :param  string file_path: 文件路径
             :return: True or False
    """
    # global m_SamplesX
    # global m_SamplesY
    # global m_SamplesZ
    # global m_SamplesV

    global file
    m_SamplesMinX = m_SamplesMinY = m_SamplesMinZ = sys.maxsize  # sys.maxsize为int类型最大值
    m_SamplesMaxX = m_SamplesMaxY = m_SamplesMaxZ = -1
    try:
        file = open(file_path)
    except OSError as error:
        print("打开文件出现错误" + str(error))
        return
    finally:
        # pass
        line = file.readline().strip()
        counts = int(line)
        line = file.readline().strip()
        if line != "4":
            return
        line = file.readline().strip()
        if line != "x":
            return
        line = file.readline().strip()
        if line != "y":
            return
        line = file.readline().strip()
        if line != "z":
            return
        line = file.readline().strip()
        if line == "":
            return
        m_SamplesX = np.full([counts], -1)
        m_SamplesY = np.full([counts], -1)
        m_SamplesZ = np.full([counts], -1)
        m_SamplesV = np.full([counts], -1)

        for i in range(0, counts):
            line = file.readline().split()
            temp_point_x = int(line[0]) - 1  # 存取的文本是1-255，但是转换成坐标之后就是0-254
            temp_point_y = int(line[1]) - 1
            temp_point_z = int(line[2]) - 1

            temp_point_v = float(line[3])
            # c_point = C3dpoint(temp_point_x, temp_point_y, temp_point_z, temp_point_v)
            # m_Samples.append(c_point)
            m_SamplesX[i] = temp_point_x
            m_SamplesY[i] = temp_point_y
            m_SamplesZ[i] = temp_point_z
            m_SamplesV[i] = temp_point_v

            if m_SamplesMinY >= temp_point_x:
                m_SamplesMinY = temp_point_x
            if m_SamplesMaxY <= temp_point_x:
                m_SamplesMaxY = temp_point_x

            if m_SamplesMinY >= temp_point_y:
                m_SamplesMinY = temp_point_y
            if m_SamplesMaxY <= temp_point_y:
                m_SamplesMaxY = temp_point_y

            if m_SamplesMinZ >= temp_point_z:
                m_SamplesMinZ = temp_point_z
            if m_SamplesMaxZ <= temp_point_z:
                m_SamplesMaxZ = temp_point_z
    file.close()
    return m_SamplesX, m_SamplesY, m_SamplesZ, m_SamplesV


def load_Ti(file_path):
    """
           加载训练图像文件
           :param string file_path: 文件路径
           :return: True or False
           """

    # global m_TiX, m_TiY, m_TiZ
    global IsHaveTi, file
    # global m_Ti

    IsHaveTi = False

    try:
        file = open(file_path)
    except OSError as error:
        print("打开文件出现错误" + str(error))
        return
    finally:
        line = file.readline()  # 文件的第一行表示的是x,yz
        line = line.replace("\n", "")
        line = line.replace("\t", " ")
        x_scale, y_scale, z_scale = line.split(" ")
        # line.split()
        m_TiX, m_TiY, m_TiZ = int(x_scale), int(y_scale), int(z_scale)
        print("=======" + str(m_TiX) + str(m_TiY) + str(m_TiZ))
        m_Ti = np.full([m_TiZ, m_TiX, m_TiY], -1.0)

        # m_Ti = [[-1.0] * m_TiZ for i in range( m_TiX) for j in range(m_TiY)]
        # print(m_Ti.size)
        cat = file.readline().strip()
        if cat != "1":
            return

        var = file.readline().strip()
        # property_information.set_property_name(var)

        value_list = []
        while 1:
            line = file.readline()
            if not line:
                break
            line = line.replace("\n", "")
            value_list.append(float(line))
        file.close()
        cnt = 0
        # print(type(value_list[cnt]))
        for k in range(0, m_TiZ):
            for i in range(0, m_TiX):
                for j in range(0, m_TiY):
                    #  找出最小值和最大值
                    # if property_information.min_value >= value_list[cnt]:
                    #     property_information.min_value = value_list[cnt]
                    # else:
                    #     pass
                    #
                    # if property_information.max_value <= value_list[cnt]:
                    #     property_information.max_value = value_list[cnt]
                    # else:
                    #     pass

                    m_Ti[k][i][j] = float(value_list[cnt])
                    cnt = cnt + 1
    IsHaveTi = True

    return m_Ti, m_TiX, m_TiY, m_TiZ


def SetPath_TI(x, y, z):
    '''
    设置模拟路径，这个点是随机的
    :param x:
    :param y:
    :param z:
    :return:返回的是一个随机
    '''
    # 设置随机路径
    size_XYZ = x * y * z
    testlist = [x for x in range(0, size_XYZ)]
    np.random.shuffle(testlist)
    return testlist


def xyz_ToPath(x, y, z, xMax, yMax):
    """
        将x,y,z利用xMax和yMax转换成一个int类型的整数
        :param x:模拟点的x
        :param y:模拟点的y
        :param z:模拟点的z
        :param xMax:
        :param yMmax:
        :return:进行运算之后的int类型整数
        """
    return z * xMax * yMax + x * yMax + y


def path_toXYZ(path, xMax, yMax):
    """

        :param path:
        :param xMax:
        :param yMax:
        :return: list列表，列表元素分别为z,x,y
        """
    xyzList = np.full([3], -1)

    xyzList[0] = path // (xMax * yMax)
    tempTi = int(path % (xMax * yMax))
    xyzList[1] = int(tempTi // yMax)
    xyzList[2] = int(tempTi % yMax)
    return xyzList


def InsertSamples(m_Sim, m_SamplesX, m_SamplesY, m_SamplesZ, m_SamplesV):
    temp_simz = len(m_Sim)
    temp_simx = len(m_Sim[0])
    temp_simy = len(m_Sim[0][0])

    if temp_simz < 1:
        return "Sim的Z层初始化失败"
    elif temp_simx < 1:
        return "Sim的X层初始化失败"
    elif temp_simy < 1:
        return "Sim的Y层初始化失败"
    print("====" + str(len(m_Sim)) + str(len(m_Sim[0])) + str(len(m_Sim[0][0])))
    for i in range(0, len(m_SamplesV)):
        tempz = m_SamplesZ[i]
        tempx = m_SamplesX[i]
        tempy = m_SamplesY[i]
        tempv = m_SamplesV[i]
        if (tempz < len(m_Sim)) and (tempx < len(m_Sim[0])) and (
                tempy < len(m_Sim[0][0])):
            m_Sim[tempz][tempx][tempy] = tempv
            # m_SimMark[tempz][tempx][tempy] = True
        else:
            return "样品位置越界!"

    return "加载成功！"


def setPath_Simul(xRadius, yRadius, zRadius):
    """
    设置模拟图像的路径
    :param xRadius:
    :param yRadius:
    :param zRadius:
    :return: 设置一个局部的变量，可以在其他地方使用全局变量
    """
    global p_PathSim
    drection1 = int(data[5])
    drection2 = int(data[3])
    drection3 = int(data[1])
    p_PathSim = np.full([drection1 * drection2 * drection3], np.nan)
    tempk = 0
    for k in range(0, drection1):
        for i in range(0, drection2):
            for j in range(0, drection3):
                # curPath =
                p_PathSim[tempk] = xyz_ToPath(i, j, k, drection2, drection3)
                tempk += 1
    # print(str(tempk)+"tempk")
    np.random.shuffle(p_PathSim)
    print(p_PathSim)
    return p_PathSim


def SetPath_TI(x, y, z):
    """
        设置模拟路径
         :param x:
        :param y:
         :param z:
         :return: int=> []
         """

    size_XYZ = x * y * z

    testlist = [x for x in range(0, size_XYZ)]
    np.random.shuffle(testlist)

    return testlist


def getEffectivePoint(_xSim, _ySim, _zSim, effectivePointX, effectivePointY, effectivePointZ,
                      effectivePointV, effectivePointDis, m_TiX, m_TiY, m_TiZ, points_size):
    xRadius = yRadius = zRadius = int(data[17])
    # 定义数据事件

    if _xSim - xRadius < 0:
        x0 = 0
    else:
        x0 = _xSim - xRadius

    # 这里将采样结果的变量转换成训练图像的的长度 (m_SimX)-->(m_TiX)
    if m_TiX - 1 < _xSim + xRadius:
        x1 = m_TiX - 1
    else:
        x1 = _xSim + xRadius

    if _ySim - yRadius < 0:
        y0 = 0
    else:
        y0 = _ySim - yRadius

    if m_TiY - 1 < _ySim + yRadius:
        y1 = m_TiY - 1
    else:
        y1 = _ySim + yRadius

    if _zSim - zRadius < 0:
        z0 = 0
    else:
        z0 = m_TiZ - zRadius

    if m_TiZ - 1 < _zSim + zRadius:
        z1 = m_TiZ - 1
    else:
        z1 = _zSim + zRadius

    # print("z0=="+str(z0)+'z1====='+str(z1))
    # 二维图像且默认是球体（关于是否其他的形状计算功能之后在行添加）
    if z0 == z1:
        cnt = int(data[19])
        raduis = int(data[17])
        # print(cnt)
        # print(raduis)
        #
        # 从内向外查找有效点（遍历、判界、判重、有效点个数达到后直接返回）
        for m in range(1, raduis + 1):
            xmin = _xSim - m
            xmax = _xSim + m
            ymin = _ySim - m
            ymax = _ySim + m
            for iX in range(xmin, xmax + 1):
                if x0 <= iX <= x1:
                    if ymin >= y0:
                        # dis =
                        # 利用numpy计算欧式距离
                        a = np.array((iX, ymin))
                        b = np.array((_xSim, _ySim))
                        dis = np.linalg.norm(a - b)
                        if dis < float(data[17]) and m_Sim[z0][iX][ymin] != -1:

                            # 计算当前的其实范围，判断是否过界,然后插入有效点
                            if iX < _xSim:
                                if points_size[0] <= (_xSim - iX):
                                    points_size[0] = _xSim - iX
                            else:
                                if points_size[1] <= (iX - _xSim):
                                    points_size[1] = iX - _xSim

                            if ymin < _ySim:

                                if points_size[2] <= (_ySim - ymin):
                                    points_size[2] = _ySim - ymin
                            else:

                                if points_size[3] <= (ymin - _ySim):
                                    points_size[3] = ymin - _ySim

                            if z0 < _zSim:

                                if points_size[4] <= (_zSim - z0):
                                    points_size[4] = _zSim - z0
                            else:

                                if points_size[5] <= (z0 - _zSim):
                                    points_size[5] = z0 - _zSim
                            effectivePointZ.append(z0)
                            effectivePointX.append(iX)
                            effectivePointY.append(ymin)
                            effectivePointV.append(m_Sim[z0][iX][ymin])
                            effectivePointDis.append(dis)
                            if len(effectivePointX) == cnt:
                                return
                            # print(effectivePointDis)
                            # print(effectivePointV)

                    if ymax <= y1:
                        a = np.array((iX, ymax))
                        b = np.array((_xSim, _ySim))
                        dis = np.linalg.norm(a - b)
                        if dis < float(data[17]) and m_Sim[z0][iX][ymax] != -1:

                            if iX < _xSim:
                                if points_size[0] <= (_xSim - iX):
                                    points_size[0] = _xSim - iX
                            else:
                                if points_size[1] <= (iX - _xSim):
                                    points_size[1] = iX - _xSim

                            if ymax < _ySim:

                                if points_size[2] <= (_ySim - ymax):
                                    points_size[2] = _ySim - ymax
                            else:

                                if points_size[3] <= (ymax - _ySim):
                                    points_size[3] = ymax - _ySim

                            if z0 < _zSim:

                                if points_size[4] <= (_zSim - z0):
                                    points_size[4] = _zSim - z0
                            else:

                                if points_size[5] <= (z0 - _zSim):
                                    points_size[5] = z0 - _zSim
                            effectivePointZ.append(z0)
                            effectivePointX.append(iX)
                            effectivePointY.append(ymax)
                            effectivePointV.append(m_Sim[z0][iX][ymax])
                            effectivePointDis.append(dis)
                            if len(effectivePointX) == cnt:
                                return
            for iY in range(ymin + 1, ymax):
                if y0 < iY < y1:
                    if xmin >= x0:
                        a = np.array((xmin, iY))
                        b = np.array((_xSim, _ySim))
                        dis = np.linalg.norm(a - b)
                        if dis < float(data[17]) and m_Sim[z0][xmin][iY] != -1:

                            if xmin < _xSim:
                                if points_size[0] <= (_xSim - xmin):
                                    points_size[0] = _xSim - xmin
                            else:
                                if points_size[1] <= (xmin - _xSim):
                                    points_size[1] = xmin - _xSim

                            if iY < _ySim:

                                if points_size[2] <= (_ySim - iY):
                                    points_size[2] = _ySim - iY
                            else:

                                if points_size[3] <= (iY - _ySim):
                                    points_size[3] = iY - _ySim

                            if z0 < _zSim:

                                if points_size[4] <= (_zSim - z0):
                                    points_size[4] = _zSim - z0
                            else:

                                if points_size[5] <= (z0 - _zSim):
                                    points_size[5] = z0 - _zSim
                            effectivePointZ.append(z0)
                            effectivePointX.append(xmin)
                            effectivePointY.append(iY)
                            effectivePointV.append(m_Sim[z0][xmin][iY])
                            effectivePointDis.append(dis)
                            if len(effectivePointX) == cnt:
                                return

                    if xmax <= x1:
                        a = np.array((xmax, iY))
                        b = np.array((_xSim, _ySim))
                        dis = np.linalg.norm(a - b)
                        if dis < float(data[17]) and m_Sim[z0][xmax][iY] != -1:

                            if xmax < _xSim:
                                if points_size[0] <= (_xSim - xmax):
                                    points_size[0] = _xSim - xmax
                            else:
                                if points_size[1] <= (xmax - _xSim):
                                    points_size[1] = xmax - _xSim

                            if iY < _ySim:

                                if points_size[2] <= (_ySim - iY):
                                    points_size[2] = _ySim - iY
                            else:

                                if points_size[3] <= (iY - _ySim):
                                    points_size[3] = iY - _ySim

                            if z0 < _zSim:

                                if points_size[4] <= (_zSim - z0):
                                    points_size[4] = _zSim - z0
                            else:

                                if points_size[5] <= (z0 - _zSim):
                                    points_size[5] = z0 - _zSim
                            effectivePointZ.append(z0)
                            effectivePointX.append(xmax)
                            effectivePointY.append(iY)
                            effectivePointV.append(m_Sim[z0][xmax][iY])
                            effectivePointDis.append(dis)
                            if len(effectivePointX) == cnt:
                                return
        # print(effectivePointX)
    # 三维图像
    else:
        pass


def GetDistances(x, y, z, templistx, templisty, templistz, effectivePointX, effectivePointY, effectivePointZ,
                 effectivePointV, effectivePointDis, m_TiZ, m_TiX, m_TiY):
    sum = 0.0
    # x = np.array([effectivePointZ, effectivePointX, effectivePointY, effectivePointV, effectivePointDis])
    length = len(effectivePointY)
    for i in range(len(effectivePointY) - 1, -1, -1):
        tempz = int(z - templistz + effectivePointZ[i])
        tempx = int(x - templistx + effectivePointX[i])
        tempy = int(y - templisty + effectivePointY[i])
        if (tempz < 0) or (tempz >= m_TiZ) \
                or (tempx < 0) or (tempx >= m_TiX) \
                or (tempy < 0) or (tempy >= m_TiY):
            effectivePointX.pop(i)
            effectivePointY.pop(i)
            effectivePointZ.pop(i)
            effectivePointV.pop(i)
            effectivePointDis.pop(i)

            continue
        if abs(effectivePointV[i] - m_Ti[tempz][tempx][tempy]) > 1e-6:
            sum += 1.0
    if len(effectivePointY) == 0:
        return -1.0
    return float(sum / len(effectivePointY))


def startSimulation(m_Ti, m_TiX, m_TiY, m_TiZ, m_Sim, m_SamplesX, m_SamplesY, m_SamplesZ, m_SamplesV, _x0,
                    _x1, _y0, _y1, _z0, _z1):
    # data[15]是否插入样例点 默认False
    if data[15]:
        results = InsertSamples(m_Sim, m_SamplesX, m_SamplesY, m_SamplesZ, m_SamplesV)
        if results != "加载成功！":
            return "加载样品失败，" + results
    # print(m_Sim[0][1][1])

    Thr = 0.0
    mindistTotal = 0.0

    # data[17]在mps_ds中表示搜索半径
    # data[9]表示对比距离的阀值
    # data[7]表示扫描比例
    m_T = float(data[9])
    m_F = float(data[7])
    temp = int(data[17])
    if temp < (m_TiX - 1) // 2:
        xRadius = temp
    else:
        xRadius = (m_TiX - 1) // 2

    if temp < (m_TiY - 1) // 2:
        yRadius = temp
    else:
        yRadius = (m_TiY - 1) // 2

    if temp < (m_TiZ - 1) // 2:
        zRadius = temp
    else:
        zRadius = (m_TiZ - 1) // 2

    scanX = m_TiX - xRadius * 2
    scanY = m_TiY - yRadius * 2
    scanZ = m_TiZ - zRadius * 2
    # print(type(data[23]))
    # is_use_same_path_size：一般默认为False
    if data[23] == "False":
        scanX = m_TiX
        scanY = m_TiY
        scanZ = m_TiZ

    p_PathSim = setPath_Simul(scanX, scanY, scanZ)
    pathTi = SetPath_TI(scanX, scanY, scanZ)
    j = 0
    # print(len(set(pathTi)))
    # print(len(set(p_PathSim)))
    time1 = time.time()
    tttt = (m_TiZ * m_TiX * m_TiY)
    points_size = [_x0, _x1, _y0, _y1, _z0, _z1]
    for i in range(0, tttt):
        start = time.time()
        mindist = 32767.0
        bestX = -1
        bestY = -1
        bestZ = -1
        templistZ, templistX, templistY = path_toXYZ(p_PathSim[i], m_TiX, m_TiY)
        # 如果当前节点是样品点的话，自动跳过
        # print(templistZ)
        if m_Sim[templistZ][templistX][templistY] != -1:
            continue
        # 获取数据样板,数据样板是动态的，需要随时添加和删除

        effectivePointX = []
        effectivePointY = []
        effectivePointZ = []
        effectivePointV = []
        effectivePointDis = []
        getEffectivePoint(templistX, templistY, templistZ, effectivePointX, effectivePointY, effectivePointZ,
                          effectivePointV, effectivePointDis, m_TiX, m_TiY, m_TiZ, points_size)
        if len(effectivePointX) == 0:
            m_Sim[templistZ][templistX][templistY] = \
                m_Ti[random.randint(0, scanZ - 1)][random.randint(0, scanX - 1)][
                    random.randint(0, scanY - 1)]
            Thr = mindistTotal / ((i + 1) * m_T * m_T)
        else:
            # xTemp = m_TiX - _x0 - _x1
            # yTemp = m_TiY - _y0 - _y1
            # zTemp = m_TiZ - _z0 - _z1
            # j = 0
            xTi = yTi = zTi = 0
            testtotal = int(scanX * scanY * scanZ * m_F)
            for m in range(testtotal):
                if j == scanX * scanY * scanZ:
                    j = 0

                if data[23] == 'False':
                    xTi = pathTi[j] // (scanY * scanZ)
                    tempTi = pathTi[j] % (scanY * scanZ)
                    yTi = tempTi // scanZ
                    zTi = int(tempTi % scanZ)

                    if xTi < points_size[0] or xTi >= m_TiX - points_size[1] or yTi < points_size[2] or yTi >= m_TiY - \
                            points_size[3] \
                            or zTi < points_size[4] or zTi >= m_TiZ - points_size[5]:
                        # print(_x0,xTi)
                        j += 1
                        continue
                # else:
                #     xTi = pathTi[j] / (scanY * scanZ) + xRadius
                #     tempTi = pathTi[j] % (scanY * scanZ)
                #     yTi = tempTi / scanZ + yRadius
                #     zTi = tempTi % scanZ + zRadius

                dis = GetDistances(xTi, yTi, zTi, templistX, templistY, templistZ, effectivePointX, effectivePointY,
                                   effectivePointZ, effectivePointV, effectivePointDis, m_TiZ, m_TiX, m_TiY)
                if dis == -1.0:
                    m_Sim[templistZ][templistX][templistY] = \
                        m_Ti[random.randint(0, scanZ - 1)][random.randint(0, scanX - 1)][
                            random.randint(0, scanY - 1)]
                    Thr = mindistTotal / (i + 1) * m_T
                    break

                elif dis <= mindist:

                    mindist = dis

                    bestX = xTi
                    bestY = yTi
                    bestZ = zTi

                if mindist <= float(Thr * (m / (scanZ * scanY * scanX * m_F))):
                    break
                # elif mindist <= 0.12:
                #     break
                # if mindistTotal > 0.01:
                #     print("=====")

                j += 1


            testmain = mindistTotal



            m_Sim[templistZ][templistX][templistY] = m_Ti[int(bestZ)][int(bestX)][int(bestY)]
            mindistTotal += mindist
            Thr = mindistTotal / ((i + 1) * m_T* m_T*m_T )
            # Thr = mindistTotal / ((i + 1) * m_T )

        end = time.time()

        # print("获取第" + str(i) + "个节点" + str(end - start))

        tempcount = int(tttt / 100)
        # if i % tempcount == 0:
        #     print("模拟的数据点" + str(i / tempcount))

    time2 = time.time()
    print(time2 - time1)


def save_Simulation(file_path, ext,m_Sim):
    """
        保存模拟图像的路径和保存的文件类型
        :param string file_path 文件路径
        :param string ext 文件类型 SGEMS or ATT
        :return: True or False
        """
    # pass
    # global scanX
    # global scanY
    # global scanZ
    scanX = int(data[1])
    scanY = int(data[3])
    scanZ = int(data[5])
    print(scanX,scanY,scanZ)

    try:
        file = open(file_path+"."+ext, 'w+')
    except OSError as error:
        print("打开文件错误" + str(error))
        return False
    finally:
        # 选择的文件类型是SGEMS
        if ext == "SGEMS":
            file.write(str(scanX) + " ")
            file.write(str(scanY) + " ")
            file.write(str(scanZ) + "\n")
            file.write("1\n")
            # file.write(self.property_information.get_property_name() + "\n")
            file.write("values" + "\n")
            for k in range(0, scanZ):
                for i in range(0, scanX):
                    for j in range(0, scanY):
                        file.write(str(m_Sim[k][i][j]) + "\n")

            # pass
            # 选择的文件类型是ATT
            # elif ext == "ATT":
            #     ni = nj = 0
            #     temp = 0
            #     file.write("-- Proper name :")
            #     # file.write(str(self.property_information.get_property_name()) + "\n")
            #     # file.write(str(self.property_information.get_property_name()) + "\n")
            #     for k in range(scanZ - 1, -1, -1):  # k 的范围是左闭右开[)
            #         for i in range(0, scanX, 1):
            #             for j in range(0, scanY, 1):
            #                 file.write(str(m_Sim[k][i][j]) + " ")
            #                 ni = ni + 1
            #                 if ni == 4:
            #                     file.write("\n")  # 控制每行输出4个
            #                     ni = 0
            #                     nj = nj + 1
            #                 if 4 > temp > 0:
            #                     j = j + 1
            #                     for j in range(j, scanY):
            #                         file.write(str(m_Sim[k][i][j]) + " ")
            #
            #                     file.write("\n")
            #                     nj = 0
            #                     pass
            #
            #     file.write("/\n")
            return True
            # pass
        # 选择的文件类型出现错误
        else:
            raise NameError("出现文件异常")
            # return False
    file.close()
    return True

def cSimulation(parameter_file):
    # for test_i in range(50):
        _x0 = _x1 = _y0 = _y1 = _z0 = _z1 = 0
        # print("输入enter键")
        # input()
    # m_TiX = m_TiY = m_TiZ = 0
        global data
        global m_Ti
        global m_Sim
        data = FileUtil.readConfigurations(parameter_file)
        print(data[27])
        # 加载训练图像
        m_Ti, m_TiX, m_TiY, m_TiZ = load_Ti(data[25])
        if m_TiX != int(data[1]):
            m_TiX = int(data[1])
        if m_TiY != int(data[3]):
            m_TiY = int(data[3])
        if m_TiZ != int(data[5]):
            m_TiZ = int(data[5])

        # 加载样品数据
        m_SamplesX, m_SamplesY, m_SamplesZ, m_SamplesV = load_Samples(data[27])
        # print(data)
        # print(m_SamplesX)
        p_PathSim = np.full([m_TiZ * m_TiX * m_TiY], -1)
        m_Sim = np.full([m_TiZ, m_TiX, m_TiY], -1)
        print(m_TiX)
        print(m_Sim)
        # 开始模拟函数
        startSimulation(m_Ti, m_TiX, m_TiY, m_TiZ, m_Sim, m_SamplesX, m_SamplesY, m_SamplesZ, m_SamplesV, _x0,
                        _x1, _y0, _y1, _z0, _z1)
        # print("模拟结束")
        # 保存模拟函数
        # print(str(test_i))
        # print(data[29].split(".")[1])
        # print( data[29].split(".")[2])
        fileData = data[29].split(".")
        print(fileData)
        # save_Simulation(fileData[0], fileData[1],m_Sim)
        save_Simulation(fileData[0], fileData[1], m_Sim)
        # print("保存文件成功，请返回")
        # Etype
        Etype.DrawEtype(fileData[0])

# if __name__ == '__main__':
#     # data中有过显示，当做全局变量
#     # m_TiX = m_TiY = m_TiZ = 0
#     # _x0 _x1数据事件中x的方位，当做全局变量
#     pass


