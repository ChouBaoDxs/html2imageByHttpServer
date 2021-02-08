import os

import requests

image_dir = 'image_dir'
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

api_url = 'http://127.0.0.1:8888/html2image'
json_data = {
    'html': '<div style="background: green;width: 200px;height: 200px"></div>',
    'crop': True,  # 是否要裁剪空白区域
    'returnBase64': True  # 是否返回 base64 字符串，默认是 False
}
res = requests.post(api_url, json=json_data)
print(res.content)
