import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image, ImageGrab
import pyautogui as pg
import time 

def concat_img_vertical(image1, image2):
    # 이미지 사이즈 참조
    width1, height1 = image1.size
    width2, height2 = image2.size

    # 두 이미지의 최대 높이, 너비를 계산
    result_width = max(width1, width2)
    result_height = height1 + height2

    # 새 이미지 객체 생성 후 두 이미지 붙여넣기
    result_image = Image.new('RGB', (result_width, result_height))
    result_image.paste(image1, (0, 0))
    result_image.paste(image2, (0, height1))

    # 결과 이미지 반환
    return result_image

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
        (460 , 1025 if idx == 1 else 377), 
        (1600, 1605),
        data_dir = os.path.join(data_dir, "screen_captures"),
        file_name = f"{idx}.png"
    )
    pg.moveTo(400, 1000)
    time.sleep(.04)
    pg.click()
    time.sleep(.04)

    pg.scroll(-737)
    time.sleep(.04) 
    after = pg.screenshot().crop((0, 100, 2400, 800))
    return before == after  # 두 스크린샷 비교

def screen_capture_loop(post_dir, post_id):
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
    
    num_imgs = len(os.listdir(os.path.join(post_dir, cur_post_dir, "screen_captures")))
    for i in range(0, num_imgs - 3, 3):
        if i + 2  > num_imgs:
            break
        image1 = Image.open(os.path.join(post_dir, cur_post_dir, f"screen_captures/{str(i + 1)}.png"))
        image2 = Image.open(os.path.join(post_dir, cur_post_dir, f"screen_captures/{str(i + 2)}.png"))
        image3 = Image.open(os.path.join(post_dir, cur_post_dir, f"screen_captures/{str(i + 3)}.png"))
        if i == 0:
            concat_img = concat_img_vertical(image1=image1, image2=image2)
            concat_img = concat_img_vertical(image1=concat_img, image2=image3)
        else:
            concat_img = concat_img_vertical(image1=concat_img, image2=image1)
            concat_img = concat_img_vertical(image1=concat_img, image2=image2)
            concat_img = concat_img_vertical(image1=concat_img, image2=image3)
    concat_img.save(os.path.join(post_dir, cur_post_dir, 'concat_screen_capture.png'))
    driver.quit()
