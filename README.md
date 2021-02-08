# html2imageByHttpServer
Python3 + Selenium + Tornado 实现将 url 或者 html 转成图片

## 使用指南
1. 安装依赖
    ```shell
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    ```
2. 根据实际情况修改 config.yml
    ```yaml
    driver_exec_path: "chromedriver" # chromedriver 可执行文件的绝对路径
    ```
3. 启动 http server：`python3 tornado_server.py`
4. 运行例子程序，查看生成的图片
    ```
    pythono3 example/url2image.py
    # 会生成图片 example/image_dir/url2image.png
   
    pythono3 example/html2image.py
    # 会生成图片 example/image_dir/html2image.png
    ```
5. 接口请求例子：
    ```python
    import requests
    
    # url 转图片
    json_data = {
        'url': 'https://www.baidu.com/',
        'crop': False,  # 是否要裁剪空白区域
        'returnBase64': True  # 是否返回 base64 字符串，默认是 False
    }
    res = requests.post('http://127.0.0.1:8888/url2image', json=json_data)
    print(res.content)
    
    # html 字符串转图片
    json_data = {
        'html': '<div style="background: green;width: 200px;height: 200px"></div>',
        'crop': True,  # 是否要裁剪空白区域
        'returnBase64': True  # 是否返回 base64 字符串，默认是 False
    }
    res = requests.post('http://127.0.0.1:8888/html2image', json=json_data)
    print(res.content)
    ```