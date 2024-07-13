import os
from screen_capture import concat_img_vertical
cur_notebook_dir = os.getcwd()
base_dir = os.getcwd()
key_dir = os.path.join(base_dir, 'keys')
data_dir = os.path.join(base_dir, 'data')
post_dir = os.path.join(data_dir, 'samples')
os.chdir(base_dir)
print(os.getcwd())

from dotenv import load_dotenv
print(load_dotenv(dotenv_path= os.path.join(key_dir, ".env")))
os.chdir(cur_notebook_dir)

def get_post_dir(post_id, post_dir = post_dir):
    ll = os.listdir(post_dir)
    for i, p in enumerate(ll):
        if str(post_id) in p:
            break
    return os.path.join(post_dir, ll[i])

##==========================================================

import base64
import re
from openai import OpenAI
from PIL import Image
import json
import time
import argparse

def encode_image(img_path):
    """
    Endoces an image to base64 string    
    """
    with open(img_path, 'rb') as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def extract_code(text):
    pattern = r'```python\s+(.*?)\s+```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    return None

def get_img_obj_by_idx(idx, img_dir):
    return Image.open(os.path.join(img_dir, f"{str(idx + 1)}.png"))

def get_concat_img_obj_by_idx(idx, img_dir):
    if idx == 0:
        img_obj1 = Image.open(os.path.join(img_dir, f"{str(idx + 1)}.png"))
        # img_obj2 = Image.open(os.path.join(img_dir, f"{str(idx + 2)}.png"))
        # return concat_img_vertical(img_obj1, img_obj2)
        return img_obj1
    elif idx > len(os.listdir(img_dir)) - 3:
        return None
    else:
        img_obj1 = Image.open(os.path.join(img_dir, f"{str(idx)}.png"))
        img_obj2 = Image.open(os.path.join(img_dir, f"{str(idx + 1)}.png"))
        return concat_img_vertical(img_obj1, img_obj2)
def get_script(post_dir):
    with open(os.path.join(cur_post_dir, 'scripts.txt'), 'r', encoding='utf-8') as tt:
        rr = tt.read()
    return rr

from openai import OpenAI

client = OpenAI()
def get_response(img_obj, script, prv_source, prv_used_script):
    prompt = f'''
    너의 임무는 입력 포스트 이미지에 있는 글을 스크립트를 참조해서 HTML 소스코드로 변환하는 거야.

    포스트 내에 있는 텍스트로 된 본문은 아래 '스크립트'와 같아.
    입력 이미지에서 스크립트를 참조해서 가장 비슷한 문장을 찾아 문장 안에 있는 텍스트를 포스트 이미지의 한줄처럼 출력하는 게 주요 임무야. 포스트 이미지와 똑같이 출력되게 HTML 형식으로 출력해줘.

    참조할 정보는 입력으로 들어간 이미지(포스트 이미지), '스크립트', '이전 소스 코드', '이전 소스코드에 사용된 스크립트 일부분'으로 총 네가지야.
    - 입력으로 들어간 이미지는 한국어로 된 블로그 포스트의 일부분이야. 이 이미지는 포스트의 첫부분일 수도, 중간부분 혹은 마지막 부분일 수도 있어.
    - '스크립트'는 전체 포스트의 내용이야. 문장으로 구성돼있으며 문장은 스크립트와 포스트 내 line break로 구분된 한 줄을 의미해. 포스트의 텍스트로 된 한 줄은 스크립트에 있는 한 문장과 연결돼.
    - '이전 소스 코드'는 이전 포스트의 일부분에서 출력된 HTML코드야. 포스트의 처음부터 현재 이미지로 들어간 부분의 이전까지 전체 변환된 HTML 소스코드를 담고 있어.
    - '이전 소스코드에 사용된 스크립트 일부분'은 이전 소스 코드에서 이미 사용한 스크립트야. 스크립트에서 이 부분은 이미 사용됐기에 이미지에 포함되어 있다고 하더라도 변환할 필요가 없어.


    결과물은 '출력 소스 코드'와 '사용한 스크립트', '현재까지 사용한 전체 스크립트' 세개야. 다른 부가 설명 없이 파이썬 json모듈에 넣으면 바로 되게끔 JSON형식으로 세개의 출력을 생성해줘. 
    - '출력 소스 코드'는 '이전 소스 코드'를 참고해서 일관되게 작성해줘. 새로 생성된 코드만 담아줘.


    다음은 '출력 소스 코드'를 생성할때 지켜야 할 사항이야.

    - 포스트 내 문자로 된 한 줄은 무조건 스크립트에 있는 문장들 중 하나여야 해. 스크립트에 없는 문장은 중간 구분선인 <hr>과 같은 기호들이 아닌 이상 문자로서 출력의 구성 요소가 되지 않아.
    - 문장이 Heading으로 보이는 경우 적당히 사이즈가 맞는 레벨의 Heading <h숫자>를 적용해줘.
    - 문장이 heading이 아닌 경우 출력에서 각 문장 사이에 <center>문장 내용</center>의 형식으로 태그를 넣어줘
        예를 들어 문장의 내용이 "우연히 발견한 가게이다!" 라면 "<center>우연히 발견한 가게이다!</center>"로 나와야 해

    - 포스트 내 있는 이미지는 마크다운 본문 내 ((이미지 내용)) 으로 처리해서 작성해줘.
        - ((이미지 내용))안에는 이미지가 무엇인지 짧게 묘사해줘.

    - 문장안에 이모지가 있는 경우 최대한 비슷한 이모지를 넣어줘.

    - 본문 중간에 구분선이 있는 경우 <hr> 로 구분선을 넣어줘.

    - 본문 이미지 내 특정 문장이나 단어에 스타일이 적용된 경우 inline CSS 스타일로 똑같이 나오게끔 구성해줘.
        - 예를 들어 '테이블 위에 사람들이 음식을 즐기는 모습'에서 '테이블 위'에만 배경색이 지정됐고 폰트는 볼드 처리 됐다면 <p style="text-align: center;" data-ke-size="size16"><span style="background-color: #9feec3;"><b>테이블 위</b></span> 에 사람들이 음식을 즐기는 모습</p>로 지정해줄 수 있어

    - 포스트 내 있는 이미지는 마크다운 본문 내 ((이미지 내용)) 으로 처리해서 작성해줘.
        - ((이미지 내용))안에는 이미지가 무엇인지 짧게 묘사해줘.
        - 사진 이미지가 아닌 캐릭터 이미지는 무시해줘.

    - 완성된 소스코드는 사람이 알아보기 쉽게 prettify 해줘. 각 줄이 한줄로 구분되게 해줘.

    ## 참조할 정보

    *스크립트
    {script}

    *이전 소스 코드
    {prv_source}

    *이전 소스코드에 사용된 스크립트 일부분
    {prv_used_script}
    
    ## 출력할 정보
    
    *출력 소스 코드
    
    *사용한 스크립트
    
    *현재까지 사용한 전체 스크립트
    '''
    response = client.chat.completions.create(
        model = 'gpt-4o',
        response_format={"type": "json_object"},
        messages = [
                {
                    'role': 'user',
                    'content' : [
                        {
                            'type': 'text',
                            'text': prompt
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url' : f'data:image/png;base64,{img_obj}'
                            }
                        }
                    ]
                }
            ],
        max_tokens=4096
    )

    return response.to_dict()['choices'][0]['message']['content']


# get_img_obj_by_idx(24, os.path.join(cur_post_dir,"screen_captures")).save(os.path.join(cur_post_dir,"screen_captures/temp.png"))
def generate(img_idx, cur_post_dir, script, prv_result_dict = None):
    img_dir = os.path.join(cur_post_dir,"screen_captures")
    if img_idx == 0:
        concat_img = Image.open(os.path.join(img_dir, f"{str(img_idx + 1)}.png"))
    elif img_idx > len(os.listdir(img_dir)) - 3:
        return None
    else:
        img_obj1 = Image.open(os.path.join(img_dir, f"{str(img_idx)}.png"))
        img_obj2 = Image.open(os.path.join(img_dir, f"{str(img_idx + 1)}.png"))
        concat_img = concat_img_vertical(img_obj1, img_obj2)

    concat_img.save(os.path.join(cur_post_dir,"temp.png")) # 이어 붙인 이미지를 임시 이미지로 저장
    img_obj = encode_image(os.path.join(cur_post_dir,"temp.png")) # 인코딩 된 이미지 객체
    script = get_script(cur_post_dir) # 스크립트 가져오기
    result = get_response( # 실제 분석을 위한 openai API 호출
        img_obj=img_obj,
        script = script,
        prv_source = '' if img_idx == 0 else prv_result_dict['출력 소스 코드'],
        prv_used_script = '' if img_idx == 0 else prv_result_dict['현재까지 사용한 전체 스크립트']
    )
    # print(result)
    try:
        result_dict = json.loads(result)
    except:
        print(result)

    return result_dict

parser = argparse.ArgumentParser()
parser.add_argument('--post_id', required=True, help='포스트 ID 입력')
args = parser.parse_args()

post_id = args.post_id 
# post_id = 223447304536 #223439599137
cur_post_dir = get_post_dir(post_id)

result_dict = None
codes = list()
script = get_script(cur_post_dir)
start = time.time()
prv = time.time()
for i in range(len(os.listdir(os.path.join(cur_post_dir, "screen_captures"))) - 2):
    try:
        result_dict = generate(i, cur_post_dir=cur_post_dir, script = script, prv_result_dict=result_dict)
        cur_code = "".join(result_dict['출력 소스 코드']) if type(result_dict['출력 소스 코드']) == list else result_dict['출력 소스 코드']
        codes.append(cur_code)
        current = time.time()
        print("current_index: ", i, "\t", "Elapsed tiem: ", current - prv, 'TOTAL spent time: ', current - start)
        # print(result_dict)

        prv = current
        result_dict['출력 소스 코드'] = "".join(codes)
    except:
        continue


with open(os.path.join(cur_post_dir, "codes.txt"), "wb") as code_txt:
    for c in codes:
        code_txt.write(c.encode("utf8"))
    code_txt.close()

# print(result_dict['출력 소스 코드'])