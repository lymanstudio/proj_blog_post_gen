from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
import argparse
import os

cur_notebook_dir = os.getcwd()
base_dir = os.getcwd()
key_dir = os.path.join(base_dir, 'keys')
data_dir = os.path.join(base_dir, 'data')
post_dir = os.path.join(data_dir, 'posts')
sample_dir = os.path.join(data_dir, 'samples')
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
def get_script(dir):
    with open(os.path.join(dir, 'scripts.txt'), 'r', encoding='utf-8') as tt:
        rr = tt.read()
    return rr
def get_cleaned_code(dir):
    with open(os.path.join(dir, 'cleaned_code.txt'), 'r', encoding='utf-8') as tt:
        rr = tt.read()
    return rr
def get_samples(sample_dir):
    samples = []
    for i, sample in enumerate(os.listdir(sample_dir)):
        cur_sample_dir = os.path.join(sample_dir, sample)
        samples.append({
            "script": get_script(cur_sample_dir),
            "code":get_cleaned_code(cur_sample_dir),
        })
    return samples

# parser = argparse.ArgumentParser()
# parser.add_argument('--target_post_id', required=True, help='타켓 포스트 ID 입력')
# args = parser.parse_args()

post_id = 223378416577#args.post_id
cur_post_dir = get_post_dir(post_id)
script = get_script(cur_post_dir)
samples = get_samples(sample_dir=sample_dir)
llm = ChatOpenAI(model = 'gpt-4o')

template = """
    You are a powerfull assistant who convert a natural language script into a HTML codes.

    The input parameters are SCRIPTS and a few examples(a list of pairs of SCRIPT and CODE).

    The contents of HTML CODES and SCRIPTS are a set of blog post of a review of restaurants, and cafes.
    HTML CODES are a list of HTML fragments. Each element has HTML tags and contents.

    Your job is to make a trimmed and organized HTML code following the rules below.
    You can reference SCRIPT, which has pure content strings used in the HTML CODES.
    
    Here are some additional HTML rules you should follow
    - For the normal desciptive sentences, cover <center> tag to align them center.
        For example, `<center> 오늘은 스파게티를 먹는다. </center>`
    - When a header word appears, left align it, add 3 or 4 <br> tags before them, add <hr> tags after them
        - If some words like 위치, 메뉴, 시간, or 내부 appears withour any following or preceding other words, consider them as h2 headings.
        - put the following code block for headings.
        ```
        <br><br><br>
        <h2>메뉴</h2>
        <hr data-ke-style="style5"/>
        ```
    - Some codes have to have inline CSS style tags, make sure make those inline CSS styles. MAKE SURE MAKE INLINE CSS STYLES AS MANY AS POSSIBLE!
        - You have can put backgroud color or just color style.
        - You have to put inline CSS style something like this:<center> 자리가 많이 없으므로 <span style="background-color: #eff1a3;"><b>예약을 하는걸 추천</b></span>한다 📅</center>``
    - When a specific menu name appears(not the overall menu explanation), put the following HTML code blocks
        ```
        <br><br>
        <hr data-ke-style="style3"/>
        <center><h3><span style="color: darkgray; font-style: italic;"> MENU NAME </span></h3> </center>
        <hr data-ke-style="style3"/>
        <br><br>
        ```
    - If there are some misspells in the SCRIPT, correct them.
    - Make sure put <br> tags inbetween lines if needed, for the visibility.
    - At the end of SCRIPT, if something like ```<center>내돈내산 솔직후기입니다 - ☝</center>``` appears, substitute the following codes.
        ```
        <br><br><br>
        <hr data-ke-style="style1"/>
        <center><h4><span style="color: darkgray; font-style: bold;"> 내돈내산 솔직후기입니다 - ☝</span></h4> </center>
        <br><br>
        ```
    - If the content is a simple list or just address, not a descriptive type, change it to a code that lists using bullet points such as,
        ```
        <ul>
        <li>코엑스점 : 서울 강남구 테헤란로87길 46 오크우드 프리미어코엑스 센터 B2 2A11호</li>
        <li>대치본점 : 서울 강남구 선릉로72길 13 1층 파이어벨</li>
        </ul>
        ```
    - To further edit, MAKE SURE put "\n" between code lines(not <br>) to print the output in the python console and to copy/paste to the other editor.


    스크립트에 있는 말을 똑같이 쓰지 말고 조금씩 바꿔줘야한다. 
    어순을 다르게 하거나 다른 단어를 쓰되 뉘앙스와 말투는 같아야 한다.

    SCRIPT:
    {script}

    HTML CODES(your output):
"""

sample_prompt = PromptTemplate(
    input_variables=["script", "code"], template="SCRIPT: {script}\nHTML CODES: {code}"
)
# print(example_prompt.format(**samples[0]))


prompt = FewShotPromptTemplate(
    examples=samples,
    example_prompt=sample_prompt,
    suffix=template,
    input_variables=["script"],
)

final_prompt = prompt.format(script=script)
print(llm.predict(final_prompt))
