import matplotlib.pyplot as plt
import numpy as np
from Nexullance_IT import Nexullance_IT
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.DDF import DDFtopo
import globals as gl
import copy
# from joblib import Parallel, delayed

import time
start_time = time.time()

