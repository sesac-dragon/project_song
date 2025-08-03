import streamlit as st
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv
import os

#스꾸
os.makedirs(".streamlit", exist_ok=True)
with open(".streamlit/config.toml", "w") as f:
    f.write("""[theme]
primaryColor = "#BCD0E2"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#222B52"
font = "sans serif"
""")
    
# 제목
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='font-size:45px; color: #262F60;'>Google Scholar 논문 검색</h1>
        <p style='font-size:23px; color: #262F60;'>SJR 랭킹 & 인용횟수 기반 논문 검색 결과✨</p>
    </div>
""", unsafe_allow_html=True)
st.set_page_config(layout="wide")

# 사이드바
with st.sidebar:
    st.write("✨🪐🌟🌙🌩☀")
    st.write("거인의 어깨에")
    st.write("올라서서")
    st.write("더 넓은 세상을")
    st.write("바라보라")
    st.write("-- 아이작 뉴턴 --")
    st.write("✨🪐🌟🌙🌩☀")

    side_options = [5, 6, 7, 8, 9]
    num_sides = st.radio("화면 비율", side_options)
    font_scale = st.slider("글자 크기:", 1, 10, value=2)

# 레이아웃
col1, col2 = st.columns([num_sides, 10 - num_sides])

#전체 폰트 사이즈 조절
font_style = f"""
    <style>
    .custom-text {{
        font-size: {font_scale * 5}px;
        line-height: 1.6;
    }}
    input {{
        font-size: {font_scale * 5}px;
    }}
    </style>
"""
st.markdown(font_style, unsafe_allow_html=True)

# 컬럼1
with col1:
    st.markdown('<div class="custom-text"> </div>', unsafe_allow_html=True)
    
    st.markdown("""
    <style>
        input[aria-label="구글이 만든 쿠기, 나를 위해 구웠지 🍪"] {
            font-size: 7px;
            height: 18px;
        }
        div:has(>div>input[aria-label="구글이 만든 쿠기, 나를 위해 구웠지 🍪"]) {
            height: 1rem
        }
    </style>
    """, unsafe_allow_html=True)

    # 사용자 쿠키 입력
    cookies = st.text_input("구글이 만든 쿠기, 나를 위해 구웠지 🍪")
    
    st.link_button(
        "google scholar",
        "https://scholar.google.co.kr/schhp?hl=ko&as_sdt=0,5",
         help=None,
         type="secondary",
         use_container_width=False)
    
    # 데이터 프레임
    def google_scholar(query: str, num_pages: int) -> pd.DataFrame :
        q = query.replace(' ', '+')
        result = []
        for page in range(num_pages):
            try:
                start = page * 10
                res=requests.get(f'https://scholar.google.com/scholar?start={start}&q={q}&hl=en&as_sdt=0,5', headers={
                    'user-agent': 'Mozilla/5.0',
                    'cookie': cookies})
                time.sleep(3)

                soup = BeautifulSoup(res.text, 'html.parser')
                feeds = soup.select('div#gs_res_ccl_mid > div.gs_r.gs_or.gs_scl')
            
                for feed in feeds:
                    try:
                        info = feed.attrs.get('data-cid') or feed.attrs.get('data-aid')
                        res2 = requests.get(f'https://scholar.google.com/scholar?q=info:{info}:scholar.google.com/&output=cite&scirp=0&hl=en', headers={
                            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                            'cookie': cookies})
                        time.sleep(2)

                        soup2 = BeautifulSoup(res2.text, 'html.parser')
                        journer_tag = soup2.select_one('div.gs_citr > i')
                        journers = journer_tag.text if journer_tag else ''

                        day = feed.select_one('div.gs_a')
                        publish = re.search(r'\d{4}', day.text).group() if day and re.search(r'\d{4}', day.text) else ''

                        title_tag = feed.select_one('h3.gs_rt')
                        titles = re.sub(r'\[.+?\]', '', title_tag.text) if title_tag else ''

                        short_tag = feed.select_one('div.gs_rs')
                        shorts = short_tag.text if short_tag else ''

                        cite_tags = feed.select('.gs_fl.gs_flb > a')
                        cites = cite_tags[2].text.split()[-1] if len(cite_tags) > 2 else '0'

                        link_tag = title_tag.find('a') if title_tag else None
                        links = link_tag['href'] if link_tag else ''

                        temp = {
                            '논문명': titles,
                            '요약': shorts,
                            '인용수': int(cites),
                            '저널명': journers,
                            '발행년도': publish,
                            '주소': links
                        }
                        result.append(temp)

                    except Exception as e:
                        print(f"비상 ! 개별 논문 크롤링 중 에러: {e}")
                        continue

            except Exception as e:
                print(f"비상 ! {page}페이지 크롤링 중 에러 : {e}")
                continue

        return pd.DataFrame(result)

    #매칭
    def matches (search_df: pd.DataFrame, journal_df: pd.DataFrame) -> pd.DataFrame : 
        
        sjr_list = []
        
        for v1 in search_df['저널명']:
            for v2 in journal_df.iloc: # 행을 가져옴
                
                new_v1 = re.sub(r'[^a-z0-9]', '', v1.lower().strip())
                new_v2 = re.sub(r'[^a-z0-9]', '', v2['저널명'].lower().strip())
                
                if new_v1[:40] == new_v2[:40] or new_v1[-40:] == new_v2[-40:] :
                    print (f" 찾았다! {v1} 쌍둥이 {v2['저널명']}")
                    sjr_list.append(v2['SJR'])
                    break
            else:
                sjr_list.append(0)

        search_df = search_df.copy()
        search_df['SJR'] = sjr_list

        return search_df
            
    query = st.text_input("검색어를 입력하세요", value="Artificial intelligence")
    pages = st.number_input("몇 페이지까지 검색할까요?", min_value=1, max_value=50, value=1, step=1)

# 검색 버튼 클릭 시 데이터 저장
    st.markdown("""
        <style>
        .small-button {
            display: inline-block;
            padding: 0.3rem 0.6rem;
            margin-right: 0.3rem;
            font-size: 0.8rem;
            border-radius: 6px;
            background-color: #BCD0E2;
            color: black;
            text-decoration: none;
            border: 1px solid #999;
            }
        .small-button:hover {
            background-color: #a8c4d8;
        }
        </style>
        """, unsafe_allow_html=True)
    
    search_clicked = False
    clear_clicked = False

    # 버튼 UI
    btn_cols = st.columns([1, 1, 1])
    with btn_cols[0]:
        if st.button("검색 시작", key="search_btn"):
            search_clicked = True
    with btn_cols[1]:
        if st.button("검색 초기화", key="clear_btn"):
            clear_clicked = True
    with btn_cols[2]:
        st.link_button("sci-hub", "https://sci-hub.se/", use_container_width=True)

    
# 검색 시작 시
if search_clicked:
    df = google_scholar(query, pages)
    st.success(f"총 {len(df)}개의 논문이 수집되었습니다.")

    journal_df = pd.read_csv('./jounal_score.csv')
    df_with_sjr = matches(df, journal_df)

    df_sorted = df_with_sjr.sort_values(by=["SJR", "인용수"], ascending=[False, False]).reset_index(drop=True)

    st.session_state.df_sorted = df_sorted
    st.session_state.selected_index = 0  # 선택 초기화

# 초기화 버튼 동작
if clear_clicked:
    for key in ['df_sorted', 'selected_index']:
        st.session_state.pop(key, None)
    st.session_state.refresh_token = time.time()  

# 검색 결과가 세션에 있을 경우
if "df_sorted" in st.session_state:
    df_sorted = st.session_state.df_sorted

    # 선택 인덱스 초기화
    if "selected_index" not in st.session_state:
        st.session_state.selected_index = 0

    # 논문 제목 리스트 생성
    paper_titles = [f"{row['논문명']} ({row['발행년도']})" for _, row in df_sorted.iterrows()]

    # selectbox 항상 실행
    selected_title = st.selectbox("논문을 선택하세요", paper_titles, index=st.session_state.selected_index)
    st.session_state.selected_index = paper_titles.index(selected_title)

    # 논문 리스트 표시
    st.dataframe(df_sorted[['논문명', '저널명', '발행년도','인용수','SJR']], use_container_width=True)

    #상세정보
    with col2:
        selected_row = df_sorted.iloc[st.session_state.selected_index]
        st.markdown('<div class="custom-text"><h3>논문 세부정보</h3></div>', unsafe_allow_html=True)
        st.markdown(f"<div class='custom-text'><b>저널명:</b> {selected_row['저널명']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='custom-text'><b>발행년도:</b> {selected_row['발행년도']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='custom-text'><b>요약:</b> {selected_row['요약']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='custom-text'><b>인용수:</b> {selected_row['인용수']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='custom-text'><b>SJR:</b> {selected_row['SJR']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='custom-text'><a href='{selected_row['주소']}' target='_blank'>DOI</a></div>", unsafe_allow_html=True)


#제목
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='font-size:45px; color: #262F60;'>논문 추천 GPT 챗봇 💭</h1>
    </div>
""", unsafe_allow_html=True)

#gpt api
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

user_input = st.text_input("검색어:")

if "messages" not in st.session_state:
    st.session_state.messages = []

gpt_col1, gpt_col2 = st.columns([1, 1], gap="small")
with gpt_col1:
    gpt_clicked = st.button("알려줘 GPT", use_container_width=True)

with gpt_col2:
    clear_gpt = st.button("내용 초기화", use_container_width=True)

# GPT 버튼 클릭 시 처리
if gpt_clicked and user_input:
    keyword = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": user_input})

    prompt_messages = [
        {"role": "user", "content":
        f"""You're a helpful assistant for recommending papers based on the user's search intent.
            You should analyze the papers found to accurately figure out what the user wants.
            The accuracy of the search results is determined by the frequency of search terms in user's search server paper summaries.
            You should recommend papers sorted by journal impact factor score and citation count.

            Use a scoring system: 
            +8 for high citation, 
            +9 points for high SJR, 
            +8 for {keyword} relevance.

            If there are no direct matches, recommend papers that are contextually relevant.
            Show summaries with each DOI source, each journal name and published years when recommending papers.
            Suggest more than 5 papers.
        
            Tone: Friendly and professional."""},

        {"role": "user", "content": f"""Your searching keyword is {keyword}."""}
            ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=prompt_messages,
        max_tokens=1000,
        temperature=0.1,
        stream=False
    )

    gpt_reply = response.choices[0].message.content.strip()
    st.session_state.messages.append({"role": "assistant", "content": gpt_reply})

# 초기화 버튼 처리
if clear_gpt:
    st.session_state.messages = []

#gpt 출력
for msg in st.session_state.messages:
    st.markdown(f"<div style='font-size:{font_scale * 5}px'><b>{msg['role'].capitalize()}</b>: {msg['content']}</div>", unsafe_allow_html=True)
