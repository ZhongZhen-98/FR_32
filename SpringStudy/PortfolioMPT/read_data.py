import pandas as pd
import csv
import numpy as np
import MPT_Module as mptm
import matplotlib.pyplot as plt

df = mptm.read_data(252)


df_ann_returns, df_ann_returns_cov = mptm.cal_rtnrisk(df)

print(df_ann_returns, df_ann_returns_cov)