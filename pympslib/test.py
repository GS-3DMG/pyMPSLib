import os

import numpy as np

from pympslib.DS import save_Simulation

m_Sim = np.full([10, 10, 10], -1)
file_name, file_extension = os.path.splitext("./a.txt")
# print(fileData)
# save_Simulation(fileData[0], fileData[1],m_Sim)
# save_Simulation(file_name, file_extension, m_Sim)
try:
    # if not os.path.exists(file_name):
    #     os.makedirs(file_name)
    file = open(file_name + "." + file_extension, 'w+')
except OSError as error:
    print("打开文件错误" + str(error))
    print(2)
# finally:
#     print(1)