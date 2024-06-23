from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
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
def get_script(post_dir):
    with open(os.path.join(post_dir, 'scripts.txt'), 'r', encoding='utf-8') as tt:
        rr = tt.read()
    return rr
def get_codes(post_dir):
    with open(os.path.join(post_dir, 'codes.txt'), 'r', encoding='utf-8') as tt:
        rr = tt.read()
    return rr

parser = argparse.ArgumentParser()
parser.add_argument('--post_id', required=True, help='포스트 ID 입력')
args = parser.parse_args()

post_id = args.post_id #223439599137 #223447304536
cur_post_dir = get_post_dir(post_id)
script = get_script(cur_post_dir)
codes = get_codes(cur_post_dir)

llm = ChatOpenAI(model = 'gpt-4o')

template = """
    You are a powerfull assistant who edits HTML codes.

    The input parameters are CODES and SCRIPTS.

    The contents of CODES and SCRIPTS are a set of blog post of a review of restaurants, and cafes.
    CODES are a list of HTML fragments. Each element has HTML tags and contents. Some element's content is duplicated with another element's.
    Some codes has inline CSS style tags, make sure leave those inline styles. MAKE SURE LEAVE INLINE CSS STYLES AS MANY AS POSSIBLE!
    There are some captions for images in the middle of CODE elements. Those image captions are not in the SCRIPT, do not erase and leave them as-is.
    If there are some unnecessary keywords, such as '\n', erase them.

    Your job is to edit CODES into a trimmed and organized HTML code where contents are not duplicated to one another.
    You can reference SCRIPT, which has pure content strings used in the CODES.
    
    Here are some additional HTML rules you should follow
    - When Header tags appears, left align it, add 3 or 4 <br> tags before them, add <hr> tags after them
        - If some words like 위치, 메뉴, 시간, or 내부 appears withour any following or preceding other words, consider them as h2 headings.
        - put the following code block for headings.
        ```
        <br><br><br>
        <h2>메뉴</h2>
        <hr data-ke-style="style5"/>
        ```
    - When a specific menu name appears(not the overall menu explanation), put the following HTML code blocks
        ```
        <br><br>
        <hr data-ke-style="style3"/>
        <center><h3><span style="color: darkgray; font-style: italic;"> MENU NAME </span></h3> </center>
        <hr data-ke-style="style3"/>
        <br><br>
        ```
    - If there are some misspells in content, correct them.
    - Make sure put <br> tags inbetween lines if needed, for the visibility.
    - At the end of OUTPUT, if something like ```<center>내돈내산 솔직후기입니다 - ☝</center>``` appears, substitute the following codes.
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

    The output should follow the rule: {instruction}

    CODES:
    {codes}

    SCRIPT:
    {script}

    Your OUTPUT:
"""

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field

# 자료구조 정의 (pydantic)
class CleandCode(BaseModel):
    script: str = Field(description="Original Script")
    cleaned_codes: str = Field(description="Cleaned HTML codes")

# 출력 파서 정의
output_parser = JsonOutputParser(pydantic_object=CleandCode)

format_instructions = output_parser.get_format_instructions()

prompt = PromptTemplate(
    template = template,
    input_variables = ["codes", "script"],
    partial_variables = {"instruction": format_instructions},
)

chain = {
    "codes" :  itemgetter("codes") | RunnablePassthrough()
    , "script" : itemgetter("script") | RunnablePassthrough()
} | prompt | llm | output_parser


fin_res = chain.invoke(
    {
        "codes" : codes,
        "script" : script
    }
)

# print(fin_res['cleaned_codes'])
with open(os.path.join(cur_post_dir,"cleaned_code.txt"), "wb") as cleaned_code:
    cleaned_code.write(fin_res['cleaned_codes'].encode("utf8"))
    cleaned_code.close()