import base64
from io import BytesIO
import os
import time
from types import MethodType
import typing
import uuid
import yaml

from PIL import Image, ImageOps
from selenium import webdriver

from tornado.web import Application, RequestHandler
import tornado.ioloop
import tornado.escape

with open('config.yml', encoding='utf-8') as f:
    config: dict = yaml.safe_load(f)
driver_exec_path = os.getenv('DEIVER_EXEC_PATH') or config.get('driver_exec_path') or 'chromedriver'

PWD = os.path.dirname(os.path.abspath(__file__))
HTML_SAVE_DIR = os.path.join(PWD, 'html_dir')
if not os.path.exists(HTML_SAVE_DIR):
    os.makedirs(HTML_SAVE_DIR)


def crop_image_margin(img_fileobj: typing.Union[BytesIO, str, bytes], padding=(0, 0, 0, 0)) -> bytes:
    """
    裁剪图片的白边
    :param img_fileobj: 泛指一个类文件对象，比如 BytesIO 就可以
    :param padding: 如果担心检测出来的 bbox 过小，可以加点 padding
    :return: bytes
    """
    with BytesIO(b'') as output_bf:
        if isinstance(img_fileobj, bytes):
            new_img_fileobj = BytesIO()
            new_img_fileobj.write(img_fileobj)
            new_img_fileobj.seek(0)
            img_fileobj = new_img_fileobj
        image = Image.open(img_fileobj).convert('RGB')
        ivt_image = ImageOps.invert(image)
        bbox = ivt_image.getbbox()
        left = bbox[0] - padding[0]
        top = bbox[1] - padding[1]
        right = bbox[2] + padding[2]
        bottom = bbox[3] + padding[3]
        cropped_image = image.crop([left, top, right, bottom])
        cropped_image.save(output_bf, format='PNG')
        ret = output_bf.getvalue()
    return ret


def url_2_image_content(driver: webdriver.Chrome, driver_get_url: str, crop: bool = True) -> bytes:
    """
    :param driver_get_url: 能够被 driver.get 方法打开的 url，可以是网址 url，或者是本地文件地址
        eg：
            1. https://www.baidu.com/
            2. file:///opt/projects/xxx.html
    :param crop: 是否要裁剪空白区域
    :return: 图片的二进制数据
    """
    driver.get(driver_get_url)
    scroll_width = driver.execute_script('return document.body.parentNode.scrollWidth')
    scroll_height = driver.execute_script('return document.body.parentNode.scrollHeight')
    driver.set_window_size(scroll_width, scroll_height)
    image_content: bytes = driver.get_screenshot_as_png()
    if crop:
        image_content = crop_image_margin(image_content)
    return image_content


def init_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path=driver_exec_path, chrome_options=options)
    return driver


class MainHandler(RequestHandler):
    def get(self):
        self.write('Hello, world')


class Url2ImageHandler(RequestHandler):
    def post(self):
        data: dict = tornado.escape.json_decode(self.request.body)
        url: str = data['url']
        crop: bool = data.get('crop', True)
        return_base64: bool = data.get('returnBase64', False)
        image_content = self.application.driver.url_2_image_content(url, crop)
        # self.set_header('Content-Type', 'image/png')
        if return_base64:
            image_content = 'data:image/png;base64,' + base64.b64encode(image_content).decode()
        self.write(image_content)


class Html2ImageHandler(RequestHandler):
    def post(self):
        data: dict = tornado.escape.json_decode(self.request.body)
        html_str: str = data['html']
        crop: bool = data.get('crop', True)
        return_base64: bool = data.get('returnBase64', False)
        html_file_name = f'{int(time.time() * 1000)}-{uuid.uuid4()}.html'
        html_file_abspath = os.path.join(HTML_SAVE_DIR, html_file_name)
        with open(html_file_abspath, 'w', encoding='utf8') as f:
            f.write(html_str)
        file_url = f'file://{html_file_abspath}'
        image_content = self.application.driver.url_2_image_content(file_url, crop)
        # self.set_header('Content-Type', 'image/png')
        if return_base64:
            image_content = 'data:image/png;base64,' + base64.b64encode(image_content).decode()
        self.write(image_content)


def make_app() -> Application:
    return Application([
        (r'/', MainHandler),
        (r'/url2image', Url2ImageHandler),
        (r'/html2image', Html2ImageHandler),
    ])


if __name__ == '__main__':
    app: Application = make_app()
    driver = init_driver()
    setattr(driver, 'url_2_image_content', MethodType(url_2_image_content, driver))
    setattr(app, 'driver', driver)
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
