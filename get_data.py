import pymupdf
import os
import argparse
import json

from selenium.webdriver.chrome.options import Options
from screen_capture import *

base_dir = os.getcwd()
key_dir = os.path.join(base_dir, 'keys')
data_dir = os.path.join(base_dir, 'data')
pdf_dir = os.path.join(data_dir, 'pdf')
post_dir = os.path.join(data_dir, 'posts')
img_dir = os.path.join(data_dir, 'images')
text_dir = os.path.join(data_dir, 'texts')
print(base_dir)

def merge_strings(strings):
    def find_overlap(a, b):
        # a의 접미사와 b의 접두사가 최대로 겹치는 부분을 찾는다.
        max_overlap = 0
        overlap_end = 0
        # a의 접미사와 b의 접두사를 비교하여 겹치는 최대 길이를 찾는다.
        for i in range(1, min(len(a), len(b)) + 1):
            if a[-i:] == b[:i]:
                max_overlap = i
                overlap_end = i
        return max_overlap, overlap_end

    while len(strings) > 1:
        max_len = -1
        max_i, max_j = 0, 0
        max_overlap_end = 0
        # 모든 쌍에 대해 최대 겹침을 찾는다.
        for i in range(len(strings)):
            for j in range(len(strings)):
                if i != j:
                    overlap_len, overlap_end = find_overlap(strings[i], strings[j])
                    if overlap_len > max_len:
                        max_len = overlap_len
                        max_i, max_j = i, j
                        max_overlap_end = overlap_end
        # 최대 겹침이 있는 쌍을 병합한다.
        if max_len > 0:
            strings[max_i] = strings[max_i] + strings[max_j][max_overlap_end:]
            strings.pop(max_j)
        else:
            break

    return strings

def reindex_images(post_dir, post_id):
    ll = os.listdir(post_dir)
    for i, p in enumerate(ll):
        if str(post_id) in p:
            print(p)
            break
    cur_post_dir = ll[i]
    # print(os.listdir(os.path.join(post_dir, cur_post_dir, 'images')))
    for i, img_name in enumerate(os.listdir(os.path.join(post_dir, cur_post_dir, 'images'))):
        os.rename(os.path.join(post_dir, cur_post_dir, 'images', img_name), \
            os.path.join(post_dir, cur_post_dir, 'images', str(i).rjust(2, '0') + ".png"))
        
parser = argparse.ArgumentParser()
parser.add_argument('--file_name', required=True, help='실행할 PDF 파일 이름, 확장자 제외')
args = parser.parse_args()
docs = pymupdf.open(os.path.join(pdf_dir, f'{args.file_name}.pdf'))

base_url = "http://blog.naver.com/ddunidubab"

cur_post_id = prv_post_id = ''
cur_text_blocks = []
for idx, page in enumerate(docs):
    if base_url in page.get_text_blocks()[0][4]:
        post_meta_dict = dict()
        ## Get Post metadata
        post_meta = page.get_text_blocks()[0][4].split("\n")
        post_meta_dict["post_datetime"] = post_meta[0].replace("/", "-")
        post_meta_dict["post_date"] = post_meta_dict["post_datetime"].split()[0]
        post_meta_dict["post_time"] = post_meta_dict["post_datetime"].split()[1]
        post_meta_dict["post_id"] = post_meta[1].split("/")[-1]
        post_meta_dict["post_url"] = post_meta[1]
        post_meta_dict["post_category"] = ''.join(list(dict.fromkeys(page.get_text_blocks()[2][4].split("\n"))))
        post_meta_dict["post_title"] = ''.join(list(dict.fromkeys(page.get_text_blocks()[1][4].split("\n"))))
        

        file_name = post_meta_dict["post_date"] + "_" + post_meta_dict["post_id"]  + "_" + post_meta_dict["post_title"]
        cur_path = os.path.join(post_dir, file_name).replace("/", "_").replace("?", "").strip()
        if idx == 0:
            prv_path = cur_path
        
        if os.path.exists(cur_path) == False:
            os.mkdir(cur_path)
        with open(os.path.join(cur_path, "metadata.txt"), "wb") as meta_txt:
            for k, v in post_meta_dict.items():
                meta_txt.write(f"{k}: {v}".encode("utf8"))
                meta_txt.write(bytes((12,)))
            meta_txt.close()
        
        with open(os.path.join(cur_path, "metadata.json"), "w") as meta_json:
            json.dump(post_meta_dict, meta_json)
            meta_json.close()

        if idx == 0:
            cur_post_id = prv_post_id = post_meta_dict['post_id']
        else:
            cur_post_id = post_meta_dict['post_id']
        first_page = True
        print(idx, post_meta_dict["post_title"])
        print(cur_path, prv_path, '\n')
    


    ## 스크립트 export 영역
    if prv_post_id != cur_post_id and len(os.listdir(prv_path)) < 6:
        with open(os.path.join(prv_path, "scripts.txt"), "wb") as scripts_txt:
            for j, block in enumerate(cur_text_blocks):
                if block[0][-1] == "?":
                    cur_txt = block[0][:-1]
                else:
                    cur_txt = block[0]
                cur_txt = cur_txt + "\n"
                scripts_txt.write(cur_txt.encode("utf8"))
            scripts_txt.close()
        
        ## 스크립트를 저장할 때 스크린 캡처도 같이 진행
        screen_capture_loop(post_dir, prv_post_id)
        reindex_images(post_dir, prv_post_id)
        cur_text_blocks = []


    for k, b in enumerate(page.get_text_blocks()):
        if k == len(page.get_text_blocks()) - 1:
            continue
        elif first_page == True and k < 3: # 본 페이지가 첫 페이지일 경우 3번째 블록까지는 스킵(제목 등 본문은 아님)
            continue
        else:
            cur_text = list(dict.fromkeys(b[4].split("\n")[:-1])) # 중복된 문장 제거, 마지막 빈칸 제거
            if len(cur_text) > 1: # 문장들 사이에 겹침이 생기면 문장이 1개 이상이 됨, 겹친것 제거 후 한문장으로
                cur_text = merge_strings(cur_text) 
            cur_text_blocks.append(cur_text)
        prv_path = cur_path

    ## 사진 export 영역
    for image_index, img in enumerate(page.get_images(), start=1): # enumerate the image list
        xref = img[0] # get the XREF of the image
        pix = pymupdf.Pixmap(docs, xref) # create a Pixmap

        if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

        if os.path.exists(os.path.join(cur_path, 'images')) == False:
            os.mkdir(os.path.join(cur_path, 'images'))
        pix.save(os.path.join(cur_path, f'images/img_{str(idx).rjust(2, "0")}_{image_index}.png')) # save the image as png
        pix = None

    first_page = False
    
    prv_post_id = cur_post_id

## 마지막 포스트의 스크립트와 스크린캡처 진행
with open(os.path.join(cur_path, "scripts.txt"), "wb") as scripts_txt:
    for j, block in enumerate(cur_text_blocks):
        if block[0][-1] == "?":
            cur_txt = block[0][:-1]
        else:
            cur_txt = block[0]
        cur_txt = cur_txt + "\n"
        scripts_txt.write(cur_txt.encode("utf8"))
    scripts_txt.close()
screen_capture_loop(post_dir, cur_post_id)
reindex_images(post_dir, cur_post_id)

