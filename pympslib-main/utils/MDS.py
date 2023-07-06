import os
import numpy as np
from matplotlib import pyplot as plt
from sklearn import manifold


def load_reference_model_image(filepath):
    """
    读取SGEMS参考模型
    :param filepath: 文件路径
    :return: 返回笛卡尔网格模型
    """
    file = open(filepath)
    value_list = []
    scale = ''
    cnt = 0
    for line in file:
        if cnt == 0:
            scale = line
        elif cnt >= 3:
            value_list.append((float(line)))
        cnt = cnt + 1
    scale_list = scale.split(' ')
    x = int(scale_list[0])
    y = int(scale_list[1])
    z = int(scale_list[2])
    image = np.reshape(value_list, [z, y, x])
    for k in range(0, z):
        for i in range(0, y):
            for j in range(0, x):
                # normalize
                # if image[k, i, j] >= 127.5:
                #     image[k, i, j] = 1
                # else:
                #     image[k, i, j] = 0
                image[k, i, j] = image[k, i, j]
                # if image[k, i, j] == 1:
                #     image[k, i, j] = 255
                # else:
                #     image[k, i, j] = 0
    image_out = image
    # image_show = np.expand_dims(image.astype(np.uint8), axis=2)
    # cv2.imshow("training_image", image_show)
    # cv2.waitKey(0)
    return image_out


def get_file_name(file_dir):
    roots, dir, files = [], [], []
    for root, dirs, file in os.walk(file_dir):
        roots.append(root)
        dir.append(dirs)
        # if os.path.splitext(file)[1] == '.sgems':
        files.append(file)
    return roots, dir, files


def get_data_from_dir(path, batch_size, num):
    data = np.full([num, batch_size], -1)
    cnt = 0
    roots, dirs, files = get_file_name(path)
    print(files)
    for f in files[0]:
        filepath = path + str(f)
        sample = load_reference_model_image(filepath)
        data[cnt] = sample.flatten()
        cnt = cnt + 1
        if cnt == num:
            return data
    return data

def DrawMDS(paths, batch_size, num, save_path_mds, scale = 200):
    """

    :param paths: path list
    :param batch_size: image size
    :param num: num of each directory (each realiztions)
    :param save_path_mds: MDS save path
    :param scale:
    :return:
    """

    # 绘制二维图形
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    # 颜色集合，不同标记的样本染不同的颜色
    colors = (
        (1, 0, 0), (0, 1, 0), (0, 0, 1),
        (0.5, 0, 0), (0, 0.5, 0), (0, 0, 0.5),
        (0.5, 0.5, 0), (0, 0.5, 0.5), (0.5, 0, 0.5),
        (0.4, 0.6, 0), (0.6, 0.4, 0), (0, 0.6, 0.4),
        (0.5, 0.3, 0.2))

    data1 = get_data_from_dir(paths[0], batch_size, num)
    mds1 = manifold.MDS(n_components=2)
    X = mds1.fit_transform(data1)

    data2 = get_data_from_dir(paths[1], batch_size, num)
    mds2 = manifold.MDS(n_components=2)
    Y = mds2.fit_transform(data2)

    # print(Y)
    for i in range(0, len(X)):
        plt.scatter(X[i][0], X[i][1], color=colors[0], marker='v')
        plt.scatter(Y[i][0], Y[i][1], color=colors[1], marker='o')


    ax.set_title("MDS")
    plt.legend(["Reference", "Realizations"], loc="best")
    plt.xlim(-scale, scale)
    plt.ylim(-scale, scale)
    plt.savefig(save_path_mds)
    plt.show()
    pass

# if __name__ == "__main__":
#     TI_dir = "F:/MPSLib-Python/document/examData/result/Enesim/draw/Ti/"
#
#     """
#     ENESIM
#     """
#     ENESIM_dir = "F:/MPSLib-Python/document/examData/result/Enesim/draw/"
#     ENESIM_save_dir = ENESIM_dir + "MDS/"
#     N10I10000P1_dir = ENESIM_dir + "N10I10000/"
#     # N10I10000P1_save_dir = N10I10000P1_dir + "N10I10000/"
#     N20I3000P1_dir = ENESIM_dir + "N20I3000/"
#     # N20I3000P1_save_dir = N20I3000P1_dir + "N20I3000/"
#     N10I3000P1_dir = ENESIM_dir + "N10I3000/"
#     # N10I3000P1_save_dir = N10I10000P1_dir + "N10I3000/"
#     N10I3000P10_dir = ENESIM_dir + "N10I3000P10/"
#     # N10I3000P10_save_dir = N10I10000P1_dir + "N10I3000/"
#
#     """
#     SNESIM
#     """
#     SNESIM_dir = "F:/MPSLib-Python/document/examData/result/Snesim/draw/"
#     SNESIM_save_dir = SNESIM_dir + "MDS/"
#     t7l3_dir = SNESIM_dir + "t7l3/"
#
#     draw_multi_dimensional_scaling_map([TI_dir, N10I10000P1_dir, N20I3000P1_dir, N10I3000P1_dir, N10I3000P10_dir, t7l3_dir], 250*250*1, 50, SNESIM_save_dir + "MDS.png", 200)