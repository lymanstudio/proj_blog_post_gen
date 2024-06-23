import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageGrab
import pyautogui as pg
import time 
base_dir = os.getcwd()
key_dir = os.path.join(base_dir, 'keys')
data_dir = os.path.join(base_dir, 'data')
pdf_dir = os.path.join(data_dir, 'pdf')
post_dir = os.path.join(data_dir, 'posts')
img_dir = os.path.join(data_dir, 'images')
text_dir = os.path.join(data_dir, 'texts')

def screen_area_capture(base_win, start_point, end_point, data_dir, file_name):
    if base_win.isActive == False:
        try:
            base_win.activate()
        except:
            pass
    img = ImageGrab.grab(bbox = (start_point[0], start_point[1], end_point[0], end_point[1]))
    img.save(os.path.join(data_dir, file_name))
    # img = Image.open(os.path.join(data_dir, 'test_pil.png'))

def capture_and_compare(base_win, idx, data_dir):
    if idx == 1:
        time.sleep(2)
        if os.path.exists(os.path.join(data_dir, "screen_captures")) == False:
            os.mkdir(os.path.join(data_dir, "screen_captures"))

    before = pg.screenshot().crop((0, 100, 2400, 800))
    screen_area_capture(
        base_win, 
        (850 , 900 if idx == 1 else 377), 
        (2388, 1605),
        data_dir = os.path.join(data_dir, "screen_captures"),
        file_name = f"{idx}.png"
    )
    pg.moveTo(800, 1000)
    time.sleep(.1)
    pg.click()
    time.sleep(.1)
    # if idx == 1:
    #     pg.hotkey('ctrl', 'r')
    #     time.sleep(.2)
    pg.scroll(-737)
    time.sleep(.1) 
    after = pg.screenshot().crop((0, 100, 2400, 800))
    return before == after  # 두 스크린샷 비교


post_id = 223322440548
options = Options()
driver = webdriver.Chrome()
driver.get(f"https://blog.naver.com/ddunidubab/{post_id}")
driver.maximize_window()

base_win = pg.getWindowsWithTitle("네이버블로그")[0]
idx = 1
ll = os.listdir(post_dir)
for i, p in enumerate(ll):
    if str(post_id) in p:
        print(p)
        break
cur_post_dir = ll[i]
while not capture_and_compare(base_win, idx, data_dir = os.path.join(post_dir, cur_post_dir)):
    idx += 1
    continue