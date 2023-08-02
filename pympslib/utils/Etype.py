import os

import re
import numpy as np


def EtypeAve(dir):
    count = 0
    llist = []
    for filename in os.listdir(dir):
        # if filename.endswith(".gslib"):
        if filename.endswith(".SGEMS") or filename.endswith(".gslib"):
            count += 1
            file_dir = os.path.join(dir, filename)
            # print(file_dir)
            locals()['list' + str(count)] = []
            file = open(file_dir)
            line = file.readline()
            if count == 1:
                x,y,z = line.replace('/n', '').split(" ")
            cat = file.readline()
            var = file.readline()
            while True:
                line = file.readline().strip()
                if not line:
                    break
                locals()['list' + str(count)].append(float(line))
            file.close()
            llist.append(locals()['list' + str(count)])

        else:
            continue
    ave = list(np.mean(llist, axis=0))
    std = list(np.std(llist,axis=0))
    return ave,std,x,y,z


def EtypeWrite(path, list, x_size, y_size, z_size):
    with open(path, 'w') as file:
        file.write(
            str(x_size) + " " + str(y_size) + " " + str(z_size) + "1\nv")
        for i in range(0, len(list)):
            file.write("\n" + str(list[i]))

def MeanWrite(dir, output_file, list):

    for filename in os.listdir(dir):
        if filename.endswith(".SGEMS"):
            file_to_read = os.path.join(dir, filename)
            print(file_to_read)
            with open(file_to_read) as fr, open(output_file, "w") as fw:
                for i in range(6):
                    print(fr.readline())
                print("===========")
                for line in fr:
                    lineo = line.strip()
                    line = line.strip()
                    line = re.sub(' +',' ', line).split(' ')
                    print(line)
                    position = (int(line[1])-1)*250 + int(line[0])
                    print(position)
                    newline = lineo + "  " + str(list[position]) + "\n"
                    fw.write(newline)
            break
        if filename.endswith(".dat"):
            file_to_read = os.path.join(dir, filename)
            print(file_to_read)
            with open(file_to_read) as fr, open(output_file, "w") as fw:
                for i in range(6):
                    print(fr.readline())
                print("===========")
                for line in fr:
                    lineo = line.strip()
                    line = line.strip()
                    line = re.sub(' +',' ', line).split(' ')
                    position = int(line[1])*250 + int(line[0]) + 1
                    print(list[position])
                    print(line)
                    newline = lineo + "                 " + str(list[position]) + "\n"
                    fw.write(newline)

            break

def DrawEtype(output_dir):
    mean, std, x_size, y_size, z_size = EtypeAve(output_dir)
    # print(std,x_size, y_size, z_size)
    # 写etype-mean均值文件
    EtypeWrite(output_dir+"/etypemean.gslib",mean, x_size, y_size, z_size)
    # 写etype-std标准差文件
    EtypeWrite(output_dir+"/etypestd.gslib",std, x_size, y_size, z_size)
    # 把两个文件拖到SGeMS看看
    MeanWrite(output_dir,output_dir +"mean.txt",mean)


# if __name__ == '__main__':
#     # 把这个改成自己实验结果（50个都放在此路径下）的存放路径---记得把"\"改成“//”
#     output_dir = "F://MPSLib//document//examData//result//Ds//T0.1F0.5M20S10//"
#     # 其他什么都不用改，直接运行
#     mean, std, x_size, y_size, z_size = EtypeAve(output_dir)
#     # print(std,x_size, y_size, z_size)
#     # 写etype-mean均值文件
#     EtypeWrite(output_dir+"etypemean.gslib",mean, x_size, y_size, z_size)
#     # 写etype-std标准差文件
#     EtypeWrite(output_dir+"etypestd.gslib",std, x_size, y_size, z_size)
#     # 把两个文件拖到SGeMS看看
#     MeanWrite(output_dir,output_dir +"mean.txt",mean)