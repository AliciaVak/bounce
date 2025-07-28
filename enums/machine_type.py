from enum import Enum

class MachineType(str, Enum):
    MRI = "MRI"
    CT = "CT"
    ECG = "ECG"
