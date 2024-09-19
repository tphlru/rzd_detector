from rzd_detector.codemodules.face.respiration.mttscan.model import MTTS_CAN
import matplotlib.pyplot as plt
from scipy.signal import butter
from rzd_detector.codemodules.face.respiration.mttscan.inference_preprocess import preprocess_raw_video, detrend

import numpy as np
import scipy.io
import sys
import argparse