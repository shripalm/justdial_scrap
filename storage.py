import pandas as pd
import os

def save_to_csv(data, file):
    df = pd.DataFrame(data)
    if os.path.exists(file):
        df.to_csv(file, mode="a", header=False, index=False)
    else:
        df.to_csv(file, index=False)