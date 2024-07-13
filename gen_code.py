from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import ConfigurableField
from operator import itemgetter
import argparse
import os

cur_notebook_dir = os.getcwd()
base_dir = os.getcwd()
key_dir = os.path.join(base_dir, 'keys')
data_dir = os.path.join(base_dir, 'data')
post_dir = os.path.join(data_dir, 'tistory_post')
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

def get_scripts(sample_dir):
    samples = []
    for i, sample in enumerate(os.listdir(sample_dir)):
        cur_sample_dir = os.path.join(sample_dir, sample)
        # print(cur_sample_dir)
        samples.append({"script" : get_script(cur_sample_dir)})
    return samples

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


llm = (
    ChatAnthropic(model_name='claude-3-opus-20240229')
    .configurable_alternatives(
        ConfigurableField(id = 'llm'),
        default_key="claude3-opus",
        claude3_5_sonnet=ChatAnthropic(model_name='claude-3-5-sonnet-20240620'),
        gpt4o = ChatOpenAI(model = 'gpt-4o'),
        gpt3_5 = ChatOpenAI(model = 'gpt-3.5-turbo'),
    )
)



# print(example_prompt.format(**samples[0]))
script_template = """
    당신의 임무는 입력으로 들어오는 스크립트를 양식을 맞춰 비슷하게 바꿔 OUTPUT으로 내보내는 것이다.
    SCRIPT에 있는 말을 그대로 사용하지 않고 조금씩 바꿔줘야한다. 
    - 본문에 있는 내용은 빠짐 없이 모두 들어가야한다.
    - 뉘앙스와 말투는 같아야 한다.
        - 말투는 20대 여자가 카페나 맛집을 소개하는 말투로 조금 귀여워야 한다.
    - 문장은 무조건 존댓말을 사용한다.
    - 마침표는 쓰지 않는다. 예를 들어 '매우 조용한 공간이었습니다.'가 아닌 '매우 조용한 공간이었습니다'로 나와야한다.
    - 분위기나 음식과 관련된 문장이 나오면 관련한 이모지를 단어 뒤나 마지막에 넣어야한다.
        - 예를 들어 '우리는 고민 끝에 레드와인을 시켰다'라는 말이 나오면🍷나 🍾와 같은 이모지를 와인 단어 뒤나 문장 마지막에 넣는 것이다.  
    - OUTPUT의 포맷은 그냥 단순 텍스트여야 한다.
    - SCRIPT에 문장이 마쳐지지 않고 그냥 단어나 주소, 영업시간 등 단순 정보만 나오면 변형을 거치지 않고 그대로 내보낸다.
        - 예를 들어 "더 스팟 패뷸러스 시간", "내부", "메뉴", "월~금 10시 - 21시 50분", "서울특별시 강남구 삼성로63길 13" 와 같이 line break로 나눠졌으면서 문장이 아닌 단순 정보들은 그대로 내보낸다.
,   - 문장의 말미를 '~습니다.' 말고 '~어요'투로 생성해주고 가끔씩 자연스럽게 반말이나 단답형으로도 생성해야한다.

    SCRIPT:
    {script}
    
    OUTPUT:
"""
sample_script_prompt = PromptTemplate(
    input_variables=["script"], template="SCRIPT: {script}"
)
# script_prompt = FewShotPromptTemplate(
#     examples=get_scripts(sample_dir=sample_dir),
#     example_prompt=sample_script_prompt,
#     suffix=script_template,
#     input_variables=["script"],
# )

# parser = argparse.ArgumentParser()
# parser.add_argument('--target_post_id', required=True, help='타켓 포스트 ID 입력')
# args = parser.parse_args()

post_id = 223349588814#args.post_id
cur_post_dir = get_post_dir(post_id)
script = get_script(cur_post_dir)
samples = get_samples(sample_dir=sample_dir)

script_prompt = PromptTemplate.from_template(script_template)
script_chain = {"script" : RunnablePassthrough()} | script_prompt | llm | StrOutputParser()
subs_script_1 = script_chain.with_config(configurable={"llm": "gpt4o"}).invoke({"script" : script})
print(subs_script_1, "\n\n========================================================================\n\n")
subs_script_2 = script_chain.with_config(configurable={"llm": "claude3_5_sonnet"}).invoke({"script" : script[300:]})
print(subs_script_2, "\n\n========================================================================\n\n")


# subs_script = script_chain.with_config(configurable={"llm": "claude3-opus", "temparature": .9}).invoke({"script" : script})
# print(subs_script)
# subs_script_3 = script_chain.with_config(configurable={"llm": "claude3_haiku"}).invoke({"script" : script})
# print(subs_script, "\n\n========================================================================\n\n")

convert_template = """
    You are a powerfull assistant who convert a natural language script into a HTML codes.

    The input parameters are SCRIPTS and a few examples above(a list of pairs of SCRIPT and CODE).

    The contents of HTML CODES and SCRIPTS are a set of blog post of a review of restaurants, and cafes.
    HTML CODES are a list of HTML fragments. Each element has HTML tags and contents.

    Your job is to make a trimmed and organized HTML code following the rules below.
    You can reference SCRIPT, which has pure content strings used in the HTML CODES, but have to change the words or sentences.
    
    Here are some additional HTML rules you should follow.
    - For the normal desciptive sentences, cover <center> tag to align them center.
        - For example, `<center> 오늘은 스파게티를 먹는다. </center>`
    - Break the lines as many as possible. No more than 30 characters in a single line.
        - Event though the sentence not ended, break the line on a right spot.
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
        <center><h4><span style="color: darkgray; font-style: bold;">※ 본 포스트는 제품 및 서비스를 제공받지 않은 내돈내산 후기입니다.</span></h4> </center>
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


    (주의) SCRIPT에 있는 말을 그대로 CODE에 사용하지 말고 조금씩 바꿔줘야한다. 
    예를 들면 어순을 다르게 하거나 다른 단어를 쓰되 뉘앙스와 말투는 같아야 한다.

    SCRIPT:
    {script}

    HTML CODES(your output):
"""
sample_prompt = PromptTemplate(
    input_variables=["script", "code"], template="SCRIPT: {script}\nHTML CODES: {code}"
)
convert_prompt = FewShotPromptTemplate(
    examples=samples,
    example_prompt=sample_prompt,
    suffix=convert_template,
    input_variables=["script"],
)


# llm = ChatOpenAI(model = 'gpt-4o')
llm = ChatAnthropic(model = 'claude-3-5-sonnet-20240620')

final_prompt = convert_prompt.format(script=subs_script_2[500:])
result = llm.predict(final_prompt)

print(result)

