import os

import requests

image_dir = 'image_dir'
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

api_url = 'http://127.0.0.1:8888/url2image'
json_data = {
    'url': 'https://www.baidu.com/',
    'crop': False  # 是否要裁剪空白区域
}
res = requests.post(api_url, json=json_data)
if res.status_code == 200:
    with open(os.path.join(image_dir, 'url2image.png'), 'wb') as f:
        f.write(res.content)
else:
    print(res.content)
