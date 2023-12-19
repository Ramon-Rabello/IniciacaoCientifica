import pydicom as dicom
import matplotlib.pyplot as plt

criaimg = "./img/1.dcm"

ds = dicom.dcmread(criaimg)

plt.imshow(ds.pixel_array,cmap=plt.cm.gray)
plt.show()