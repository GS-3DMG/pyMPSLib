# pyMPSLib

## Introduction

*This project is used to update and maintain the python version of the multi-point geostatistical methods library.*

## Maintainer

Zhesi Cui zhsc0604@qq.com

Qianhong Huang 1510851768@qq.com

Cui Liu 1115759375@qq.com

Ruihong Zhou 1609199073@qq.com

Zixiao Yang 192660947@qq.com

Hongfeng Fang 1440683528@qq.com

## How To Use

### Requirements example


* python 3.8 
* numpy 1.20.1
* matplotlib 3.7.1 
* scikit-learn 1.2.2

### Installation

* You can use ` git clone https://github.com/GS-3DMG/pyMPSLib   ` to download it locally, 

* Or it can be installed from PyPi with `pip install pyMPSLib` 

### Usage

* We provide some test data in test folder and provide  a sample in test/2D/test, where you can directly run the code, 
* Alternatively,  you can use it in the following way:

```python
from pympslib import simulation

# SNESIM simulation
simulation.snesim(${PARAMETER_FILE_PATH})
# ENESIM simulation
simulation.enesim(${PARAMETER_FILE_PATH})
# DS simulation
simulation.ds(${PARAMETER_FILE_PATH})
```

### Parameter Files

For the specific parameter file format, please refer to,

 `mps_snesim.txt` `mps_snesim.txt` `mps_ds.txt`

If you want to know how to select specific parameters, please refer to

[Strebelle SB (2002) Conditional simulation of complex geological structures using multiple-point statistics. Mathematical Geology 34(1):1-21.](https://doi.org/10.1023/A:1014009426274)

[Mariethoz G, Renard P, Straubhaar J (2010) The direct sampling method to perform multiple‐point geostatistical simulations. Water Resources Research 46(11).](https://doi.org/10.1029/2008WR007621)

More parameter sensitivity analysis can be found in relevant papers in this code.
