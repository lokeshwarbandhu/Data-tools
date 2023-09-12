import requests
import cv2
from io import BytesIO
import numpy as np

data = ['OI001', 'https://metasqlstorage.blob.core.windows.net/metamaterial/Subprocess-00684/500um.jpg']
file = data[0]
id = data[1]
filename = file[0:2]+'A'+file[2:]+'.jpg'
blob = BytesIO(requests.get(id).content)
img = cv2.imdecode(np.frombuffer(blob.read(), np.uint8), 1)
cv2.imshow('a',img)
cv2.waitKey(0)
