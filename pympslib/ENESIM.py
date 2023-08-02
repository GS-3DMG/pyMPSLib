import os
import random
import datetime
import time
import numpy as np
from .entity.Coords import *
from .utils import Etype

def file_exist(filename):
    return os.path.exists(filename)
def read_TIFrom_GS3DCSV_File(filename,ti):
    file=open(filename,'r')
    if file==None:
        return False
    file.close()
def get_extension(filename):
    return filename.split(".")[1]
def oneD_To_3D(oneDIndex, dimX, dimY):
    idxZ = oneDIndex // (dimX * dimY)
    idxY = (oneDIndex - idxZ * dimX * dimY) // dimX
    idxX = oneDIndex - dimX * (idxY + dimY * idxZ)
    return [idxZ, idxY, idxX]
def read_TI_From_GSLIB_File(filename):
    ti=[]
    dimensions=[]
    if os.path.exists(filename)==False:
        return False,ti
    file = open(filename, 'r')
    if file == None:
        return False
    str = file.readline().rstrip('\n').split(' ')
    for i in str:
        dimensions.append(i)
    str = file.readline().rstrip('\n').split(' ')
    #Number of channel
    for i in str:
        number_of_channels=int(i)
    #Channel labels ...
    for i in range(number_of_channels):
        str = file.readline().rstrip('\n').split(' ')
    #Initialize TI dimensions 初始化训练图像维度
    ti=np.full([int(dimensions[2]),int(dimensions[1]),int(dimensions[0])],-1,dtype=float)
    #Putting data inside
    dataCnt = 0
    str = file.readline().strip()
    while len(str)!=0:
        if number_of_channels==1:
            dataValue=float(str[0])
        elif number_of_channels>1:
            data=[]
            while len(str)!=0:
                data.append(float(str))
        else:
            dataValue=0
        id=oneD_To_3D(int(dataCnt),int(dimensions[0]),int(dimensions[1]))
        idxX = int(id[2])
        idxY = int(id[1])
        idxZ = int(id[0])
        ti[idxZ][idxY][idxX]=dataValue/1.0
        dataCnt=dataCnt+1
        str = file.readline().strip()
    file.close()
    return True,ti

def read_harddata_from_eas_file(filename,no_data_value,data_size_x,data_size_y,
                                data_size_z,min_world_x,min_world_y,min_world_z,step_x,
                                step_y,step_z):
    if get_extension(filename)=="SGEMS":
        data = np.full([data_size_z, data_size_y, data_size_x], np.nan, dtype=float)
        if os.path.exists(filename)==False:
            return False,data
        file = open(filename, 'r')
        if file == None:
            return False,data
        str = file.readline()
        number_of_columns=int(file.readline())
        for i in range(number_of_columns):
            file.readline()
        #初始化TI维度，数据单元初始化为nan
        #Putting data inside
        str = file.readline().strip()
        #idx_x=0
        #idx_y=0
        #idx_z=0
        #coord_x=0.0
        #coord_y=0.0
        #coord_z=0.0
        #dataValue=0.0
        data_cnt=0
        while len(str)!=0:
            s=str.split(" ")
            line_data = []
            for i in range(len(s)):
                if(s[i]!=""):
                    line_data.append(float(s[i]))
            if(number_of_columns >= 4):
                #将从全局坐标读取的数据转换为局部坐标（从0,0,0和单元格大小1,1,1开始）
                coord_x=line_data[0]
                coord_y=line_data[1]
                coord_z=line_data[2]
                data_value=line_data[3]
                idx_x = (int)((coord_x - min_world_x)/step_x)-1
                idx_y = (int)((coord_y - min_world_y) / step_y)-1
                idx_z = (int)((coord_z - min_world_z) / step_z)-1
                if data_value != no_data_value:
                    if idx_x>-1 and idx_y>-1 and idx_z>-1 and idx_x<data_size_x and idx_y<data_size_y and idx_z<data_size_z:
                        data[idx_z][idx_y][idx_x]=data_value
                    else:
                        print("Hard data，{0}：Data outside simualtion grid ix,iy,iz={1}，{2}，{3}".format(filename,idx_x,idx_y,idx_z))
                else:
                    oneD_To_3D(data_cnt,data_size_x,data_size_y,idx_x,idx_y,idx_z)
                    data_cnt=data_cnt+1
                    data_value = line_data[0]
                    if(data_value!=no_data_value):
                        data[idx_z][idx_y][idx_x]=data_value
            str = file.readline().strip()
        file.close()
        return True,data
    else:
        data = np.full([data_size_z, data_size_y, data_size_x], np.nan, dtype=float)
        if os.path.exists(filename) == False:
            return False, data
        file = open(filename, 'r')
        if file == None:
            return False, data
        str = file.readline()
        number_of_columns = int(file.readline())
        for i in range(number_of_columns):
            file.readline()
        # 初始化TI维度，数据单元初始化为nan
        # Putting data inside
        str = file.readline().strip()
        # idx_x=0
        # idx_y=0
        # idx_z=0
        # coord_x=0.0
        # coord_y=0.0
        # coord_z=0.0
        # dataValue=0.0
        data_cnt = 0
        while len(str) != 0:
            s = str.split(" ")
            line_data = []
            for i in range(len(s)):
                if (s[i] != ""):
                    line_data.append(float(s[i]))
            if (number_of_columns >= 4):
                # 将从全局坐标读取的数据转换为局部坐标（从0,0,0和单元格大小1,1,1开始）
                coord_x = line_data[0]
                coord_y = line_data[1]
                coord_z = line_data[2]
                data_value = line_data[3]
                idx_x = (int)((coord_x - min_world_x) / step_x)
                idx_y = (int)((coord_y - min_world_y) / step_y)
                idx_z = (int)((coord_z - min_world_z) / step_z)
                if data_value != no_data_value:
                    if idx_x > -1 and idx_y > -1 and idx_z > -1 and idx_x < data_size_x and idx_y < data_size_y and idx_z < data_size_z:
                        data[idx_z][idx_y][idx_x] = data_value
                    else:
                        print("Hard data，{0}：Data outside simualtion grid ix,iy,iz={1}，{2}，{3}".format(filename, idx_x,
                                                                                                       idx_y, idx_z))
                else:
                    oneD_To_3D(data_cnt, data_size_x, data_size_y, idx_x, idx_y, idx_z)
                    data_cnt = data_cnt + 1
                    data_value = line_data[0]
                    if (data_value != no_data_value):
                        data[idx_z][idx_y][idx_x] = data_value
            str = file.readline().strip()
        file.close()
        return True, data
def write_to_gslib_file(filename,sg,sg_dim_x,sg_dim_y,sg_dim_z):
    a_file=open(filename,'w')
    #Header
    a_file.writelines(str(sg_dim_x)+" "+str(sg_dim_y)+" "+str(sg_dim_z))
    a_file.writelines('\n'+str(1))
    a_file.writelines('\n'+'v')
    for z in range(sg_dim_z):
        for y in range(sg_dim_y):
            for x in range(sg_dim_x):
                a_file.writelines('\n'+str(sg[z][y][x]))
    a_file.close()
def treed_to_1d(idxX,idxY,idxZ,dimX,dimY):
    one_d_index = idxX + dimX * (idxY + idxZ * dimY)
    return one_d_index
def seconds_to_hr_mn_sec(seconds,hour,minute,second):
    minute = int(seconds / 60)
    second = int(seconds % 60)
    hour = int(minute / 60)
    minute =int(minute % 60)
    return hour,minute,second
def is_nan(x):
    return x!=x
def fill_sg_from_hd( x, y, z, level, add_noddes, putback_nodes):
    pass
def _initialize_sg(sg,sg_dim_x,sg_dim_y,sg_dim_z,value=np.nan):
    for z in range(sg_dim_z):
        for y in range(sg_dim_y):
            for x in range(sg_dim_x):
                sg[z][y][x]=value
    return sg
def initilize_path(sg_dim_x,sg_dim_y,sg_dim_z,path):
    #Putting sequential indices
    value=0
    for z in range(sg_dim_z):
        for y in range(sg_dim_y):
            for x in range(sg_dim_x):
                path.append(value)
                value=value+1
    return path
def get_cpdf_from_softdata(sg_idx_x, sg_idx_y, sg_idx_z, param, soft_pdf, closet_coords):
    pass

def adding_data(grid, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, sg_idx_x, sg_idx_y, sg_idx_z, l, v):
    #print("adding data")
    #Utility.is_nan(grid[idx_z][idx_y][idx_x])!=True
    if is_nan(grid[idx_z][idx_y][idx_x])!=True:
        found_cnt[0]=found_cnt[0]+1
        if found_cnt[0]>max_neighbours_limit:
            return True
        a_coords=Coords(0,0,0)
        a_coords.setXIndex(idx_x-sg_idx_x)
        a_coords.setYIndex(idx_y-sg_idx_y)
        a_coords.setZIndex(idx_z-sg_idx_z)
        for i in range(len(l)):
            if (a_coords.getXIndex(),a_coords.getYIndex(),a_coords.getZIndex())==(l[i].getXIndex(),l[i].getYIndex(),l[i].getZIndex()):
        #if (a_coords.get_x(), a_coords.get_y(), a_coords.get_z()) in l:
                return False
        l.append(a_coords)
        v.append(grid[idx_z][idx_y][idx_x])
    return False

def search_data_in_direction(grid,direction,idx_x,idx_y,idx_z,found_cnt,max_neighbours_limit,x_offset,y_offset,z_offset,sg_idx_x,sg_idx_y,sg_idx_z,l,v,sg_dim_x,sg_dim_y,sg_dim_z):
    if direction == 0: # Direction X
        for k in range(-y_offset,y_offset+1):
            idx_y = sg_idx_y + k
            for j in range(-z_offset,z_offset+1):
                idx_z = sg_idx_z + j
            # Adding value inside viewport only
                if ((idx_x >= 0 and idx_x < sg_dim_x) and (idx_y >= 0 and idx_y<sg_dim_y) and (idx_z >= 0 and idx_z < sg_dim_z)):
                    flag =adding_data(grid, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, sg_idx_x, sg_idx_y, sg_idx_z, l, v)
                    if flag==True:
                        return idx_x, idx_y, idx_z
        return idx_x, idx_y, idx_z
    elif direction==1:#Direction Y
        for k in range(-x_offset+1,x_offset):
            idx_x = sg_idx_x + k
            for j in range(-z_offset+1,z_offset):
                idx_z = sg_idx_z + j
            # Adding value inside viewport only
                if ((idx_x >= 0 and idx_x < sg_dim_x) and (idx_y >= 0 and idx_y< sg_dim_y) and (idx_z >= 0 and idx_z < sg_dim_z)):
                    flag = adding_data(grid, idx_x, idx_y, idx_z, found_cnt,max_neighbours_limit, sg_idx_x, sg_idx_y, sg_idx_z,l, v)
                    if flag == True:
                        return idx_x, idx_y, idx_z
        return idx_x, idx_y, idx_z
    elif direction==2:#Direction Z
        for k in range(-x_offset+1,x_offset):
            idx_x = sg_idx_x + k
            for j in range(-y_offset+1,y_offset):
                idx_y = sg_idx_y + j
            # Adding value inside viewport only
                if ((idx_x >= 0 and idx_x <sg_dim_x) and (idx_y >= 0 and idx_y< sg_dim_y) and (idx_z >= 0 and idx_z < sg_dim_z)):
                    flag = adding_data(grid, idx_x, idx_y, idx_z, found_cnt,max_neighbours_limit, sg_idx_x, sg_idx_y, sg_idx_z, l, v)
                    if flag == True:
                        return idx_x, idx_y, idx_z
        return idx_x, idx_y, idx_z
def circular_search(sg_idx_x,sg_idx_y,sg_idx_z,grid,max_neighbours_limit,max_radius_limit,l,v,sg_dim_x,sg_dim_y,sg_dim_z,debug_mode):
    found_cnt=[0]
    idx_x=idx_y=idx_z=0
    max_x_offset=sg_dim_x-1
    max_y_offset=sg_dim_y-1
    max_z_offset=sg_dim_z-1
    max_dim=max(max_x_offset,max_y_offset,max_z_offset)
    #Check center point
    #Utility.is_nan(grid[sg_idx_z][sg_idx_y][sg_idx_x])
    if not is_nan(grid[sg_idx_z][sg_idx_y][sg_idx_x]):
        found_cnt[0] = found_cnt[0]+1
        a_coords=Coords(0,0,0)
        l.append(Coords(a_coords.getXIndex(),a_coords.getYIndex(),a_coords.getZIndex()))
        # l.append(a_coords)
        v.append(grid[sg_idx_z][sg_idx_y][sg_idx_x])
    #random direction
    #random_direction=0
    for i in range(1,max_dim):
        #print(i)
        #maximum neighbor count check
        if found_cnt[0]>max_neighbours_limit:
            break
        #maximum search radius check
        if i>max_radius_limit and max_radius_limit !=-1:
            break
        #Initialize offset 偏移
        x_offset = y_offset = z_offset=i
        #Get a random search direction
        random_direction = random.randint(0,0)
        # print(random_direction)
        if debug_mode>2:
            print("Random search directtion ={0}".format(random_direction))
        if random_direction==0:
            #print(0)
            # direction + X
            idx_x = sg_idx_x + x_offset
            idx_x, idx_y, idx_z=search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit,x_offset,y_offset,
                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
            # direction - X
            idx_x = sg_idx_x - x_offset
            idx_x, idx_y, idx_z=search_data_in_direction(grid, 0, idx_x, idx_y, idx_z,found_cnt, max_neighbours_limit, x_offset,y_offset,
                                          z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
            # direction + Y
            idx_y = sg_idx_y + y_offset
            idx_x, idx_y, idx_z=search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
                                          z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
            # direction - Y
            idx_y = sg_idx_y - y_offset
            idx_x, idx_y, idx_z=search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
                                          z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
            # direction +Z
            idx_z = sg_idx_z + z_offset
            idx_x, idx_y, idx_z=search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
                                          z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
            # direction -Z
            idx_z = sg_idx_z - z_offset
            idx_x, idx_y, idx_z=search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
                                          z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
            # random_direction = 1

        # if random_direction==1:
        #     #print(1)
        #     # direction + X
        #     idx_x = sg_idx_x + x_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit,x_offset,y_offset,
        #                            z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction - X
        #     idx_x = sg_idx_x - x_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction +Z
        #     idx_z = sg_idx_z + z_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction -Z
        #     idx_z = sg_idx_z - z_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction + Y
        #     idx_y = sg_idx_y + y_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction - Y
        #     idx_y = sg_idx_y - y_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        # #     random_direction = 2
        #
        # if random_direction==2:
        #     #print(2)
        #     # direction + Y
        #     idx_y = sg_idx_y + y_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction - Y
        #     idx_y = sg_idx_y - y_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction + X
        #     idx_x = sg_idx_x + x_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction - X
        #     idx_x = sg_idx_x - x_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction +Z
        #     idx_z = sg_idx_z + z_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction -Z
        #     idx_z = sg_idx_z - z_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #
        #     random_direction = 3
        #
        # if random_direction==3:
        #     #print(3)
        #     # direction + Y
        #     idx_y = sg_idx_y + y_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction - Y
        #     idx_y = sg_idx_y - y_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction +Z
        #     idx_z = sg_idx_z + z_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction -Z
        #     idx_z = sg_idx_z - z_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction + X
        #     idx_x = sg_idx_x + x_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction - X
        #     idx_x = sg_idx_x - x_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
            # random_direction = 4

        # if random_direction==4:
        #     #print(4)
        #     # direction +Z
        #     idx_z = sg_idx_z + z_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction -Z
        #     idx_z = sg_idx_z - z_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction + X
        #     idx_x = sg_idx_x + x_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction - X
        #     idx_x = sg_idx_x - x_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction + Y
        #     idx_y = sg_idx_y + y_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction - Y
        #     idx_y = sg_idx_y - y_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #
        #     random_direction = 5
        #
        # if random_direction==5:
        #     #print(5)
        #     # direction +Z
        #     idx_z = sg_idx_z + z_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction -Z
        #     idx_z = sg_idx_z - z_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 2, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction + Y
        #     idx_y = sg_idx_y + y_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction - Y
        #     idx_y = sg_idx_y - y_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 1, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction + X
        #     idx_x = sg_idx_x + x_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)
        #     # direction - X
        #     idx_x = sg_idx_x - x_offset
        #     idx_x, idx_y, idx_z=search_data_in_direction(grid, 0, idx_x, idx_y, idx_z, found_cnt, max_neighbours_limit, x_offset,y_offset,
        #                                   z_offset, sg_idx_x, sg_idx_y, sg_idx_z, l, v,sg_dim_x,sg_dim_y,sg_dim_z)


def sample_from_pdf(pdf):
    simulated_value=0.0
    random_value=float(random.uniform(0,1))
    cumsum_pdf=0.0#integral conditional probability density (conditionalPdfFromTi)
    for k,v in pdf.items():
        cumsum_pdf=cumsum_pdf+pdf[k]
        if cumsum_pdf >= random_value:
            simulated_value=k
            break
    return simulated_value
def  get_realization_from_cpdf_ti_enesim(sg,max_neighbours,sg_idx_x,sg_idx_y,sg_idx_z,level,nMax_count_cpdf,ti_dim_x,ti_dim_y,ti_dim_z,ti_path,TI,sg_dim_x,sg_dim_y,sg_dim_z,debug_mode,max_iterations,tg1,tg2,cpdf):
    #Get cPdf from training image using ENESIM style
    # conditional_pdf_from_ti={}
    get_cpdf_ti_enesim(sg,max_neighbours,sg_idx_x,sg_idx_y,sg_idx_z,level,nMax_count_cpdf,ti_dim_x,ti_dim_y,ti_dim_z,ti_path,TI,sg_dim_x,sg_dim_y,sg_dim_z,debug_mode,max_iterations,tg1,tg2,cpdf)
    simulated_value = 0.0
    # Check if any SoftData are available?
    # std::multimap<float, float> softPdf;
    soft_pdf = {}
    # decide whether soft or ti cpdf takes preference..
    closet_coords = Coords(0, 0, 0)
    if get_cpdf_from_softdata(sg_idx_x, sg_idx_y, sg_idx_z, 0, soft_pdf, closet_coords):
        pass
    simulated_value = sample_from_pdf(cpdf)
    if debug_mode > 2:
        print("simulated_value={0}".format(simulated_value))
    return simulated_value
def get_cpdf_ti_enesim(sg,max_neighbours,sg_idx_x,sg_idx_y,sg_idx_z,level,nMax_count_cpdf,ti_dim_x,ti_dim_y,ti_dim_z,ti_path,TI,sg_dim_x,sg_dim_y,sg_dim_z,debug_mode,max_iterations,tg1,tg2,cpdf):
    # max_cpdf_count = _nMax_count_cpdf
    conditional_count = {}
    cpdf_count = 0
    lc_dist_min = 32767.0  # RAND_MAX
    lc_dist_threshold = 1.0
    l = []
    v = []
    circular_search(sg_idx_x, sg_idx_y, sg_idx_z, sg, max_neighbours, -1, l, v, sg_dim_x,
                    sg_dim_y, sg_dim_z, debug_mode)
    #print(len(l))
    # 移动训练图像路径，以便选择随机起始位置
    #print(ti_path)
    ti_shift = random.randint(0, ti_dim_x * ti_dim_y * ti_dim_z - 1)
    ti_path[:] = ti_path[ti_shift:len(ti_path)] + ti_path[0:ti_shift]
    # print(ti_path)
    #random.shuffle(ti_path)
    for i_ti_path in range(len(ti_path)):
        ti_idx = oneD_To_3D(ti_path[i_ti_path], ti_dim_x, ti_dim_y)
        ti_idx_z = int(ti_idx[0])
        ti_idx_y = int(ti_idx[1])
        ti_idx_x = int(ti_idx[2])
        if debug_mode > 3:
            print("i_ti_path={0}".format(i_ti_path))
            print("  POSITION IN TI: TI_idxX={0},TI_idxY={1},TI_idxZ={2}".format(ti_idx_x, ti_idx_y, ti_idx_z))
        v_center_ti = TI[ti_idx_z][ti_idx_y][ti_idx_x]
        # matchCnt=0
        lc_dist = 0
        # ti_x=ti_y=ti_z=0
        for i in range(len(l)):
            # For each pixel relatively to the current pixel based on vector L  基于向量L，相对于当前像素的每个像素
            ti_x = ti_idx_x + l[i].getXIndex()
            ti_y = ti_idx_y + l[i].getYIndex()
            ti_z = ti_idx_z + l[i].getZIndex()
            # l_dist=abs(l[i].get_x())+abs(l[i].get_y())+abs(l[i].get_z())
            # CHECK IF WE ARE INSIDE BOUNDS!!
            if (ti_x >= 0 and ti_x < ti_dim_x) and (ti_y >= 0 and ti_y < ti_dim_y) and (ti_z >= 0 and ti_z < ti_dim_z):
                v_ti = TI[ti_z][ti_y][ti_x]
                if v_ti != v[i]:
                    # Unless we have a perfect match, a penalty distance of 1 is added.
                    lc_dist = lc_dist + 1
            else:
                # ARE OUT OF BOUNDS
                lc_dist = lc_dist + 1
        # WHAT IS THE VALUE OF AT THE CENTER NOTE IN THE TT RIGHT NOW?
        # Check if current L,T in TI match conditional observations better
        if lc_dist < lc_dist_min:
            # We have a new MIN distance
            lc_dist_min = lc_dist
            value_from_ti = v_center_ti
        # Add a count to the Cpdf if the current node match L,V according to some threshold..如果当前节点根据某个阈值匹配L，V，则向Cpdf添加计数。
        if lc_dist < lc_dist_threshold:
            cpdf_count = cpdf_count + 1
            # Update conditionalCount Counter (from which the local cPdf can be computed)
            if conditional_count.get(v_center_ti) == None:
                # Then we've encountered the word for a first time.
                # Is this slow?
                conditional_count[v_center_ti] = 1
            else:
                # Then we've already seen it before..
                conditional_count[v_center_ti] = conditional_count[v_center_ti] + 1
            # print(conditional_count)
            if debug_mode > 2:
                print("Perfect Match  i_ti_path={0}, v_center_ti={1}".format(i_ti_path, v_center_ti))
        if nMax_count_cpdf <= cpdf_count:
            if debug_mode > 1:
                print("max_cpdf_count Reached i_ti_path={0},cpdf_count={1}".format(i_ti_path, cpdf_count))
            break
        # Stop looking if we have reached the maximum number of allowed iterations in TI
        if i_ti_path > max_iterations:
            if debug_mode > 1:
                print("Max Ite Reached i_ti_path={0},nmax_ite={1}".format(i_ti_path, max_iterations))
                print("LC_dist={0}".format(lc_dist))
            break
        if debug_mode > 3:
            a = int(input("输入一个整数"))
    # END SCAN OF TI FOR CPDF
    if debug_mode > 1:
        tg1[sg_idx_z][sg_idx_y][sg_idx_x] = lc_dist_min
        tg2[sg_idx_z][sg_idx_y][sg_idx_x] = cpdf_count
    # CHECK THAT conditionalCount HAS AT LEAST ONE COUNT
    # This may not always be the case when no conditional event has been found!
    if cpdf_count == 0:
        # NO MATCHES HAS BEEN FOUND. ADD THE CURRENT BEST MACTH TO THE conditionalCount
        if conditional_count.get(value_from_ti) == None:
            # Then we've encountered the word for a first time. Is this slow?
            conditional_count[value_from_ti] = 1
        else:
            conditional_count[value_from_ti] = conditional_count[value_from_ti] + 1
    # COMPUTE ConditionalPdf from conditionalCount 从conditionalCount计算ConditionalPdf
    # Loop through all the conditional points to calculate the pdf (probability distribution function)循环遍历所有条件点以计算pdf（概率分布函数）
    # Getting the sum of counter and sort the map using the counter获取计数器和，并使用计数器对地图进行排序
    total_counter = 0.0
    for k in conditional_count.keys():
        total_counter = total_counter + conditional_count[k]
    for k, v in conditional_count.items():
        cpdf[k] = float(v) / float(total_counter)
def _simulate(sg,max_neighbours,sg_idx_x,sg_idx_y,sg_idx_z,level,nMax_count_cpdf,ti_dim_x,ti_dim_y,ti_dim_z,ti_path,TI,sg_dim_x,sg_dim_y,sg_dim_z,debug_mode,max_iterations,tg1,tg2):
    _metropolis_softdata=0
    #Soft data Metropolis integration not tested yet 软数据集成尚未测试
    if nMax_count_cpdf==1:
        _metropolis_softdata=1
    if _metropolis_softdata==1:
        cpdf = {}
        simulated_value = 0.0
        soft_pdf = {}
        #max_iterations = 100
        is_accepted = False
        closet_coords = Coords(0, 0, 0)
        if get_cpdf_from_softdata(sg_idx_x, sg_idx_y, sg_idx_z, 0, soft_pdf, closet_coords):
            pass
        else:
            get_cpdf_ti_enesim(sg, max_neighbours, sg_idx_x, sg_idx_y, sg_idx_z, level, nMax_count_cpdf, ti_dim_x,ti_dim_y, ti_dim_z, ti_path, TI, sg_dim_x, sg_dim_y, sg_dim_z, debug_mode,
                                   max_iterations, tg1, tg2,cpdf)
            simulated_value = sample_from_pdf(cpdf)
            #print(cpdf)
        return simulated_value
    else:
        cpdf = {}
        return get_realization_from_cpdf_ti_enesim(sg,max_neighbours,sg_idx_x,sg_idx_y,sg_idx_z,level,nMax_count_cpdf,ti_dim_x,ti_dim_y,ti_dim_z,ti_path,TI,sg_dim_x,sg_dim_y,sg_dim_z,debug_mode,max_iterations,tg1,tg2,cpdf)
        pass
def start_simulation(filename):
    if file_exist(filename) == False:
        print('Parameter file does not exist')
        return
    def read_line_configuration(filename):
        data = []
        with open(filename, 'r', encoding='utf-8') as file:
            str = file.readline().replace(" ", "").rstrip('\n')  # 去除空格
            while str:
                for i in str.split("#"):
                    data.append(i)
                str = file.readline().replace(" ", "").rstrip('\n')
            return data
    # Number of realizations
    data = read_line_configuration(filename)
    _realization_numbers = int(data[1])
    del data[0:2]
    # initial Value
    _seed = float(data[1])
    del data[0:2]
    # Maximum number of counts for setting up the conditional pdf
    _nMax_count_cpdf = int(data[1])
    del data[0:2]
    _max_neighbours = int(data[1])
    del data[0:2]
    # Maximum iterations 最大化迭代次数
    _max_iterations = int(data[1])
    del data[0:2]
    # Simulation Grid size X
    _sg_dim_x = int(data[1])
    del data[0:2]
    # Simulation Grid size Y
    _sg_dim_y = int(data[1])
    del data[0:2]
    # Simulation Grid size Z
    _sg_dim_z = int(data[1])
    del data[0:2]
    # Simulation Grid World min X
    _sg_world_min_x = float(data[1])
    del data[0:2]
    # Simulation Grid World min Y
    _sg_world_min_y = float(data[1])
    del data[0:2]
    # Simulation Grid World min Z
    _sg_world_min_z = float(data[1])
    del data[0:2]
    # Simulation Grid Cell Size X
    _sg_cell_size_x = float(data[1])
    del data[0:2]
    # Simulation Grid Cell Size Y
    _sg_cell_size_y = float(data[1])
    del data[0:2]
    # Simulation Grid Cell Size Z
    _sg_cell_size_z = float(data[1])
    del data[0:2]
    # TI filename
    data[1].replace(" ", "").rstrip('\n')
    _ti_filename = data[1]
    del data[0:2]
    # Output directory
    data[1].replace(" ", "").rstrip('\n')
    _output_directory = data[1]
    del data[0:2]
    # Shuffle SGPATH 随机模拟网格路径
    _shuffle_sg_path = int(data[1])
    # Shuffle Entropy Factor
    _shuffle_entropy_factor = 4
    del data[0:2]
    # Shuffle TI Path
    _shuffle_ti_path = (int(data[1]) != 0)
    del data[0:2]
    # Hard data
    data[1].replace(" ", "").rstrip('\n')
    _hardData_filenames = data[1]
    del data[0:2]
    # Hard data search radius
    _hd_search_radius = float(data[1])
    del data[0:2]
    # Softdata categories
    _softData_categories=[]
    for i in data[1].split(';'):
        _softData_categories.append(float(i))
    del data[0:2]
    # Softdata filenames
    _softData_filenames = data[1]
    del data[0:2]
    # Resize softdata grids

    # Number of threads
    _number_of_threads = int(data[1])
    del data[0:2]
    # DEBUG MODE
    _debug_mode = int(data[1])
    read_sucessfull, _TI = read_TI_From_GSLIB_File(_ti_filename)
    if read_sucessfull == False:
        print("Error reading _TI")
    dim = np.shape(_TI)
    _ti_dim_x = dim[2]
    _ti_dim_y = dim[1]
    _ti_dim_z = dim[0]
    _ti_path=[]
    # Define a random path to loop through TI cell 定义一个随机路径遍历训练图像
    _ti_path=initilize_path(_ti_dim_x, _ti_dim_y,_ti_dim_z, _ti_path)
    # if _shuffle_ti_path:
    #     random.shuffle(_ti_path)  # 打乱元素 随机生成训练图像扫描路径
        # print(_ti_path)
    if _debug_mode > -1:
        print("Number of threads:{0} ".format(_number_of_threads))
        print("Conditional points:{0} ".format(_max_neighbours))
        print("Max iterations:{0} ".format(_max_iterations))
        print("SG:{0},{1},{2} ".format(_sg_dim_x, _sg_dim_y, _sg_dim_z))
        print("TI:{0},{1},{2},{3},{4}".format(_ti_filename, _ti_dim_x, _ti_dim_y, _ti_dim_z,
                                              _TI[0][0][0]))
    if _debug_mode > -2:
        print("__________________________________________________________________________________")
        print("MPSlib: a C++ library for multiple point simulation")
        print("(c) 2015-2016 I-GIS (www.i-gis.dk) and" )
        print("              Solid Earth Geophysics, Niels Bohr Institute (http://imgp.nbi.ku.dk)")
        print("This program comes with ABSOLUTELY NO WARRANTY;")
        print("This is free software, and you are welcome to redistribute it")
        print("under certain conditions. See 'COPYING.LESSER'for details." )
        print( "__________________________________________________________________________________")
    #Intitialize random seed or not
    if _seed!=0:
        random.seed(_seed)#相同的种子
    else:
        random.seed(datetime.datetime.now())#不同的种子
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
    found1 = find_last(_ti_filename, "/")
    found2 = find_last(_ti_filename, "\\")
    found = found1 if found1 > found2 else found2
    output_filename = _output_directory + "/" + _ti_filename[found + 1:]
    #Doing the simulation
    total_secs=0.0
    #begin_realization=end_realization=0
    #end_node=0
    allocated_nodes_from_harddata=Coords(0,0,0)
    node_to_putback=Coords(0,0,0)
    #elapsed_node_secs=elapsed_realization_secs=0.0
    #node_estimated_seconds =0
    seconds=hours=minutes=0
    _sg_iterations = np.full([_sg_dim_z, _sg_dim_y, _sg_dim_x], -1, dtype=float)
    _sg = np.full([_sg_dim_z, _sg_dim_y, _sg_dim_x], -1, dtype=float)
    _simulation_path = []
    _softData_grids=[]
    read_sucessfull, _hdg = read_harddata_from_eas_file(_hardData_filenames, -999, _sg_dim_x,
                                                             _sg_dim_y, _sg_dim_z, _sg_world_min_x,
                                                             _sg_world_min_y,_sg_world_min_z,
                                                             _sg_cell_size_x, _sg_cell_size_y,
                                                             _sg_cell_size_z)
    if read_sucessfull == False and _debug_mode > -1:
        print("Error reading harddata")
    _tg1=[]
    _tg2=[]
    _total_grids_level = 0
    for n in range(_realization_numbers):
        begin_realization=time.process_time()#返回系统的当前时间和用户CPU时间的浮动值(以秒为单位)
        #Initialize the iteration count grid
        _sg_iterations=_initialize_sg(_sg_iterations,_sg_dim_x,_sg_dim_y,_sg_dim_z,0)
        #Initialize Simulation Grid from hard data or with NaN value
        _sg=_initialize_sg(_sg,_sg_dim_x,_sg_dim_y,_sg_dim_z)
        #Initialize temporary grids if debugMode is high
        if(_debug_mode>1):
            #Initialize some extra grids for extra information
            _tg1=_initialize_sg(_tg1,_sg_dim_x,_sg_dim_y,_sg_dim_z)
            _tg2=_initialize_sg(_tg2,_sg_dim_x,_sg_dim_y,_sg_dim_z)
        #offset=0
        #sg_1D_idx=0
        for level in range(_total_grids_level+1):
            #For each space level from coarse to fine 对于每个空间级别，从粗到细
            offset=int(2**level)
            #Define a simulation path for each level
            if _debug_mode>-1:
                print("Define simulation path for level {}".format(level))
            _simulation_path.clear()
            node_cnt=0
            total_nodes=(_sg_dim_x/offset)*(_sg_dim_y/offset)*(_sg_dim_z/offset)
            last_progress=0
            for z in range(_sg_dim_z):
                for y in range(_sg_dim_y):
                    for x in range(_sg_dim_x):
                        sg_1D_idx=treed_to_1d(x,y,z,_sg_dim_x,_sg_dim_y)
                        _simulation_path.append(sg_1D_idx)
                        #如果当前模拟栅格值仍然为NaN，则会发生重定位过程
                        #仅在粗略级别将硬数据移动到网格节点
                        if level!=0:
                            fill_sg_from_hd(x, y, z, level, allocated_nodes_from_harddata, node_to_putback)
                        elif level==0 and len(_hdg)!=0 and is_nan(_sg[z][y][x]):
                            #Level = 0
                            #Fill the simulation node with the value from hard data grid
                            _sg[z][y][x]=_hdg[z][y][x]
                        #Progression
                        if _debug_mode >-1 and len(_hdg)!=0:
                            node_cnt=node_cnt+1
                            #Print progression on screen
                            progress = int(node_cnt/float(total_nodes)*100)
                            if progress %10 ==0 and progress!=last_progress:#Report every 10%
                                last_progress = progress
                                print( "Relocating hard data to the simulation grid at level:{0},Progression(%):{1}".format(level,progress))
                #         x=x+offset
                #     y=y+offset
                # z=z+offset
            #if self._debug_mode > 2:
                #Shuffle simulation path indices vector for a random path
            if _debug_mode >-1:
                print("Suffling simulation path using type:{0}".format(_shuffle_sg_path))
            if len(_softData_grids)==0 and _shuffle_sg_path==2:
                print("WARNING: no soft data found, switch to random path")
                _shuffle_sg_path = 1
            if _shuffle_sg_path==1:
                random.shuffle(_simulation_path)
            #elif self._shuffle_sg_path>1:

                #Performing the simulation
                #For each value of the path
            progress_cnt=0
                #sg_idx_x=sg_idx_y=sg_idx_z=0
            if _debug_mode>-1:
                print("Simulating ")
                #Cleaning the allocated data from the SG
                #_clearSGFromHD(allocatedNodesFromHardData)
            # print(len(_simulation_path))
            random.shuffle(_ti_path)
            for i in range(len(_simulation_path)):
                    #Get node coordinates
                idx=oneD_To_3D(_simulation_path[i],_sg_dim_x,_sg_dim_y)
                sg_idx_z=int(idx[0])
                sg_idx_y=int(idx[1])
                sg_idx_x=int(idx[2])
                if is_nan(_sg[sg_idx_z][sg_idx_y][sg_idx_x]):
                    _sg[sg_idx_z][sg_idx_y][sg_idx_x]=_simulate(_sg,_max_neighbours,sg_idx_x,sg_idx_y,sg_idx_z,level,_nMax_count_cpdf,_ti_dim_x,_ti_dim_y,_ti_dim_z,_ti_path,_TI,_sg_dim_x,_sg_dim_y,_sg_dim_z,_debug_mode,_max_iterations,_tg1,_tg2)
                if _debug_mode>-1:
                        #Doing the progression
                        #Print progression on screen
                    progress=int(progress_cnt/float(total_nodes)*100)
                    progress_cnt=progress_cnt+1
                    if progress % 5 == 0  and  progress != last_progress:
                        last_progress=progress
                        end_node=time.process_time()
                        elapsed_node_secs=float(end_node-begin_realization)
                        node_estimated_seconds= int(elapsed_node_secs/float(progress_cnt)*float(total_nodes-progress_cnt))
                        hours,minutes,seconds=seconds_to_hr_mn_sec(node_estimated_seconds, hours, minutes, seconds)
                        if progress>0:
                            print("Level:{0},Progression:{1}%,finish in:{2}h{3}mn{4}sec".format(level,progress,hours,minutes,seconds))
                        pass
                    #Performing simulation for non NaN value ...
            # if _debug_mode>2:
            #     write_to_gslib_file(output_filename+"after_simulateing"+str(n)+'_level_'+str(level)+".gslib",self._sg,self._sg_dim_x,self._sg_dim_y,self._sg_dim_z)
            #     print("After relocation")
            def show_sg():
                for z in range(_sg_dim_z):
                    print("Z:{0}/{1}".format(z + 1, _sg_dim_z))
                    for y in range(_sg_dim_y):
                        for x in range(_sg_dim_x):
                            chars = [" ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                                     "a", "A", "b", "B", "c", "C", "d", "D", "e", "E", "f", "F", "g", "G", "h", "H",
                                     "i", "I", "j", "J", "k", "K", "l", "L", "m", "M", "n", "N", "p", "P", "q", "Q",
                                     "r", "R", "s", "S", "t", "T", "u", "U", "v", "v", "w", "W", ",", ";", ".", ":",
                                     "-", "_", "+", "/", "*", "<", ">", "!", "#", "&", "(", ")", "=", "?"]
                            print(chars[int(_sg[z][y][x] % len(chars))], end="")
                        print()
                    print()
            # if level!=0:
            #     self.clear_sg_from_hd(allocated_nodes_from_harddata, node_to_putback)
            # if self._debug_mode>2:
            #     write_to_gslib_file(output_filename + "after_simulateing" +str(n)  + '_level_' + str(level) + ".gslib",self._sg, self._sg_dim_x, self._sg_dim_y, self._sg_dim_z)
            #     print("After cleaning relocation")
            #     self.show_sg()
            # if self._debug_mode>2:
            #     write_to_gslib_file(output_filename + "test_sg" + str(n) + '_level_' + str(level) + ".gslib",self._sg, self._sg_dim_x, self._sg_dim_y, self._sg_dim_z)
        if _debug_mode>0:
            show_sg()
        if _debug_mode>-1:
            end_realization=time.process_time()
            elapsed_realization_secs = float(end_realization - begin_realization)
            total_secs=total_secs+elapsed_realization_secs
            print( "Elapsed time (sec): {0}    total:{1}".format(elapsed_realization_secs,total_secs))
        if _debug_mode>-2:
            # Write result to file
            if _debug_mode>-1:
                print("Write simulation grid to hard drive...")
            write_to_gslib_file(output_filename + "_sg_" + str(n) + ".gslib", _sg, _sg_dim_x,_sg_dim_y, _sg_dim_z)
            #IO.write_to_grd3_file(output_filename + "_sg_gs3d" + str(n) + ".gsd3", self._sg, self._sg_dim_x,self._sg_dim_y, self._sg_dim_z,self._sg_world_min_x,self._sg_world_min_y,self._sg_world_min_z,self._sg_cell_size_x,self._sg_cell_size_y,self._sg_cell_size_z,3)
            #Write temporary grids to  file
        if _debug_mode>1:
            write_to_gslib_file(output_filename + "_temp1_" + str(n) + ".gslib", _tg1, _sg_dim_x,_sg_dim_y, _sg_dim_z)
            write_to_gslib_file(output_filename + "_temp2_" + str(n) + ".gslib", _tg2, _sg_dim_x,_sg_dim_y, _sg_dim_z)
        #Write random path to file
        if _debug_mode>1:
            write_to_gslib_file(output_filename + "_path_" + str(n) + ".gslib", _simulation_path, _sg_dim_x,_sg_dim_y, _sg_dim_z)

    if _debug_mode>-1:
        seconds_to_hr_mn_sec(int(total_secs/_realization_numbers),hours,minutes,seconds)
        print("Total simulation time：{0}s".format(total_secs))
        print("Average time for {0} simulations: hours:{1} minutes:{2} seconds):{3} ".format(_realization_numbers,hours,minutes,seconds))
    if _debug_mode>-1:
        print("Number of threads: {0}".format(_number_of_threads))
        print("Conditional points:{0}".format(_max_neighbours))
        print("Max iterations: {0}".format(_max_iterations))
        print( "SG: {0} {1} {2}".format(_sg_dim_x,_sg_dim_y,_sg_dim_z))
        print("TI:{0} {1} {2} {3} {4}".format(_ti_filename,_ti_dim_x,_ti_dim_y,_ti_dim_z,_TI[0][0][0]))

    # Etype.DrawEtype(_output_directory)


# if __name__ == '__main__':
#     start_simulation("mps_genesim.txt")
#     input("  ")