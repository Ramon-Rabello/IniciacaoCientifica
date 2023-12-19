import pydicom as dicom

criaimg = "./img/1.dcm"

ds = dicom.dcmread(criaimg)
print(dir(ds))