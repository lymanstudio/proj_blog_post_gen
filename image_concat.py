from PIL import Image
import os

import os
os.chdir("c:\\Users\\thdwo\\Documents\\Github\\proj_blog_post_gen")
base_dir = os.getcwd()
key_dir = os.path.join(base_dir, 'keys')
data_dir = os.path.join(base_dir, 'data')
pdf_dir = os.path.join(data_dir, 'pdf')
tistory_post_dir = os.path.join(data_dir, 'tistory_post')
sample_dir = os.path.join(data_dir, 'samples')
img_dir = os.path.join(data_dir, 'images')
text_dir = os.path.join(data_dir, 'texts')

post_id = 223318279913
ll = os.listdir(tistory_post_dir)
for i, p in enumerate(ll):
    if str(post_id) in p:
        print(p)
        break
cur_post_dir = ll[i]

def concat_imgs(post_dir, cur_post_dir, img_indices: list, buffer = 60, save = False):
    # 이미지 객체들 불러오기
    imgs = []
    for idx in img_indices:
        img_idx = str(idx).rjust(2, '0') # 이미지 인덱스를 스트링으로 만든 후 rpad 주기
        imgs.append(Image.open(os.path.join(post_dir, cur_post_dir, f"images/{img_idx}.png")))
    if len(imgs) == 2:
        # 이미지 사이즈 참조
        width1, height1 = imgs[0].size
        width2, height2 = imgs[1].size

        # 두 이미지의 최대 높이, 너비를 계산
        result_width = width1 + width2 + buffer
        result_height = max(height1, height2)

        # 새 이미지 객체 생성 후 두 이미지 붙여넣기
        result_image = Image.new('RGB', (result_width, result_height), 'white')
        result_image.paste(imgs[0], (0, 0))
        result_image.paste(imgs[1], (width2 + buffer, 0))
    elif len(imgs) == 4:
        buffer = 30
        # 상반 두개
        width1, height1 = imgs[0].size
        width2, height2 = imgs[1].size
        result_width = width1 + width2 + buffer
        result_height = max(height1, height2)
        result_image1 = Image.new('RGB', (result_width, result_height), 'white')
        result_image1.paste(imgs[0], (0, 0))
        result_image1.paste(imgs[1], (width2 + buffer, 0))

        # 하반 두개
        width1, height1 = imgs[2].size
        width2, height2 = imgs[3].size
        result_width = width1 + width2 + buffer
        result_height = max(height1, height2)
        result_image2 = Image.new('RGB', (result_width, result_height), 'white')
        result_image2.paste(imgs[2], (0, 0))
        result_image2.paste(imgs[3], (width2 + buffer, 0))


        width1, height1 = result_image1.size
        width2, height2 = result_image2.size
        result_width = max(width1, width2)
        result_height = height1 + height2 + buffer

        result_image = Image.new('RGB', (result_width, result_height), 'white')
        result_image.paste(result_image1, (0, 0))
        result_image.paste(result_image2, (0 , height2 + buffer))

    else:
        return None
    
    if save:
        result_image.save(os.path.join(post_dir, cur_post_dir, f"images/processed_{img_indices[0]}.png"))
    # 결과 이미지 반환
    return result_image