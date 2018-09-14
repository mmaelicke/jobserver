"""
This is an Example Process. It will read a timeseries and return a summary of
some statistical moments and numbers
"""
import pandas as pd
import time
import random


def summary(df):
    if isinstance(df, str):
        df = pd.read_csv(df)
    time.sleep(random.randint(1, 5))
    return df.describe()


if __name__=='__main__':
    import sys

    res = summary(sys.argv[1])
    print(res)
