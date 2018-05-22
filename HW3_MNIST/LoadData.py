import numpy as np

def LoadData(path):
    Data = np.loadtxt(open(path, 'r'), delimiter=',', skiprows=1, dtype=np.int)
    Labels = Data[:, 0]
    Data = Data[:, 1:785]  # N*784
    print(Data)
    return [Data, Labels]

