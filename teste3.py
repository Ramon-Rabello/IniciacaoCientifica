import matplotlib.pyplot as plt
import pydicom
from pydicom.data import get_testdata_files
filename = "./img/7.dcm"
ds = pydicom.dcmread(filename)
plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
plt.show()


