"""
This is an Example Process. It will read a timeseries and return a summary of
some statistical moments and numbers
"""
import pandas as pd
import time
import random


def summary(df_or_filepath):
    if isinstance(df_or_filepath, str):
        df = pd.read_csv(df_or_filepath)
    elif isinstance(df_or_filepath, pd.DataFrame):
        df = df_or_filepath

    time.sleep(random.randint(1, 5))
    return df.describe()


if __name__ == '__main__':
    import sys

    try:
        res = summary(sys.argv[1])
    except Exception as e:
        res = str(e)
    finally:
        print(res)
