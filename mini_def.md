```py
#크롤링 함수화
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

def google_scholar(query: str, num_pages: int) -> pd.DataFrame :
    q = query.replace(' ', '+')
    cookie = cookies
    result = []
    for page in range(num_pages):

    try:
        start = page * 10 
        res = requests.get(f'https://scholar.google.com/scholar?start={start}&q={q}&hl=en&as_sdt=0,5', headers={
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'cookie': 'cookies'
        })
        time.sleep(3)

        soup = BeautifulSoup(res.text, 'html.parser')
        feeds = soup.select('div#gs_res_ccl_mid > div.gs_r.gs_or.gs_scl')
        print('현재 결과 수', len(feeds))

        for feed in feeds:
            try:
                info = feed.attrs.get('data-cid') or feed.attrs.get('data-aid')
                res2 = requests.get(f'https://scholar.google.com/scholar?q=info:{info}:scholar.google.com/&output=cite&scirp=0&hl=en', headers={
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                    'cookie': 'cookies'
                })
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

import pandas as pd
import re

#매핑 함수화
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

#gpt api 함수화
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
    
def format_papers_for_gpt(df: pd.DataFrame) -> str:
    context = ""
    for i, row in df.iterrows():
        context += f"{i+1}. 제목: {row['논문명']}\n요약: {row['요약']}\n인용수: {row['인용수']}, 저널: {row['저널명']}, SJR: {row['SJR']}\n\n"
        if i >= 10:
            break
    return context

if st.button("Send") and user_input:
    keyword = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": user_input})
    formatted_context = format_papers_for_gpt(df_sorted)
    
    # GPT prompt
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
        temperature=0.5,
        stream=False
    )

    gpt_reply = response.choices[0].message.content.strip()
    st.session_state.messages.append({"role": "assistant", "content": gpt_reply})

if st.button("다시 검색 & 추천"):
    df = google_scholar(query, pages)
    df_with_sjr = matches(df, journal_df)
    df_sorted = df_with_sjr.sort_values(by=["SJR", "인용수"], ascending=[False, False])
    formatted_context = format_papers_for_gpt(df_sorted)