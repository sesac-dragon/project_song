import streamlit as st
import seaborn as sb
import matplotlib.pyplot as plt
from matplotlib import rc
import pandas as pd
import plotly.graph_objects as go
import os
import json
import requests
import time
import ast
from collections import Counter
import pymysql
from datetime import datetime
from dotenv import load_dotenv


def get_db_connection():
    return pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='test1234',
        database='zigzag',
        charset='utf8mb4',
        autocommit=True
    )
conn = get_db_connection()

st.set_page_config(layout="wide") 

###**사이드바 UI**##
with st.sidebar:    
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT6w_QiMcvFqiwF7oPR3ct8S-Wkm-6TwzNkHA&s", use_container_width=True)
    st.markdown("""
    <h1 style='text-align: center;'>
    뷰티 AI 리뷰 분석
    </h1>
    """, unsafe_allow_html=True)

    def get_product_list():
        conn = get_db_connection()
        product_list = []
        try:
            with conn.cursor() as cur:
                for product_num in [1, 2, 3]:  
                    cur.execute(f"""
                        SELECT id, name FROM tb_product_{product_num}
                        ORDER BY id DESC LIMIT 5
                    """)
                    results = cur.fetchall()
                    product_list.extend([(r[0], r[1], product_num) for r in results])
            return product_list
        finally:
            conn.close()

    products = get_product_list()

    selected = st.selectbox(
        "",
        options=products,
        format_func=lambda x: f"상품{x[2]} - {x[1]} (ID:{x[0]})"
    )

    selected_id = selected[0]          # 행 ID
    selected_name = selected[1]        # 상품명
    selected_product = selected[2] # 테이블 번호
#----------------------------컬럼1-----------------------------

col1, col2, col3 = st.columns([1, 4, 2])

with col1:
    try:
        # 선택된 상품 데이터만 가져오기
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, shop_name, name, original_price, discount_price, original_image
                FROM tb_product_{selected_product}
                ORDER BY id DESC LIMIT 1
            """)
            result = cur.fetchone()
            
            if result:
                product = {
                    'product_num': selected_product,
                    'id': result[0],
                    'shop_name': result[1], 
                    'name': result[2],
                    'original_price': result[3],
                    'discount_price': result[4],
                    'image': result[5]
                }
                
                # 이미지 보여주기
                if product['image']:
                    st.image(product['image'], width=200)
                
                # 상품 정보 보여주기
                st.write(f"브랜드:{product['shop_name']}")
                st.write(f"상품명:{product['name']}")
                
                # 가격 보여주기 
                if product['original_price'] and product['discount_price']:
                    st.write(f"판매가: {int(product['original_price']):,}원")
                    st.write(f"할인가: {int(product['discount_price']):,}원")
                else:
                    price = product['discount_price'] or product['original_price']
                    if price:
                        st.write(f"판매가: {int(price):,}원")
                st.write("---")
            else:
                st.write("상품 데이터 없음.")

    except Exception as e:
        st.error(f"오류 발생 : {e}")

    # 별점 매기기
    def show_rating(product_num):
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT rates FROM tb_review_{product_num}
                    WHERE rates IS NOT NULL
                """)
                results = cur.fetchall()
            if results:
                ratings = [float(r[0]) for r in results]
                avg_rating = sum(ratings) / len(ratings)
                st.write(f"⭐ {avg_rating:.1f}점 ")
            else:
                st.write("평점 데이터가 없습니다.")
        except Exception as e:
            st.error(f"{e}")
    
    show_rating(selected_product) 
    # 키워드 긍정/중립/부정 분석 데이터 가져오기

    def get_sentiment_data(product_num):
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                SELECT 
                    SUM(CASE WHEN key_analysis LIKE '%긍정 : 1%' THEN 1 ELSE 0 END) as positive,
                    SUM(CASE WHEN key_analysis LIKE '%부정 : -1%' THEN 1 ELSE 0 END) as negative, 
                    SUM(CASE WHEN key_analysis LIKE '%중립 : 0%' THEN 1 ELSE 0 END) as neutral,
                    COUNT(*) as total
                FROM tb_key_analysis_{product_num};
                """)
                result = cur.fetchall()
                return {                
                    'positive': int(result[0][0] or 0),
                    'negative': int(result[0][1] or 0),
                    'neutral': int(result[0][2] or 0), 
                    'total': int(result[0][3] or 0)
                }
        except Exception as e:
            return {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}
    
    sentiment_data = get_sentiment_data(selected_product)

    st.markdown(
        f"""
        <div style="display:flex; gap:20px; justify-content:space-around; font-size:16px;">
            <div>전체<br><b>{sentiment_data['total']}</b></div>
            <div>긍정<br><b>{sentiment_data['positive']}</b></div>
            <div>부정<br><b>{sentiment_data['negative']}</b></div>
            <div>중립<br><b>{sentiment_data['neutral']}</b></div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.link_button("바로가기", f"https://zigzag.kr/catalog/products/{product['id'] if 'product' in locals() else selected_product}", help=None, type="secondary", icon=None, disabled=False, use_container_width=True)

#----------------------------컬럼2-----------------------------

with col2:
    def get_emotion_data(table_name, product_num):
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT emo_analysis FROM {table_name}")
                rows = cur.fetchall()
            
            cate_counter = Counter()
            total_cate = 0
            
            for (emo_str,) in rows:
                try:
                    # dict 문자열을 파이썬 dict로 변환
                    d = ast.literal_eval(emo_str)
                    cate_counter.update(d)
                    total_cate += 1
                except:
                    continue
            
            # 퍼센트 계산
            cate_percentage = {}
            for key, count in cate_counter.items():
                cate_percentage[key] = (count / total_cate) * 100 if total_cate > 0 else 0
            
            return cate_percentage, cate_counter
        
        except Exception as e:
            return {}, Counter()

    percentage_data, counter_data = get_emotion_data(f'tb_emotion_{selected_product}', selected_product)

    def create_single_category_pie(positive_percent, category_name, product_name):    
        negative_percent = 100 - positive_percent
        
        labels = ['긍정', '부정']
        values = [positive_percent, negative_percent]
        colors = ["#FF32956C", "#6FC1FF88"]
        
        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.4,  
            marker_colors=colors,
            textinfo='percent',
            textfont_size=12,
            showlegend=True
        ))
        
        fig.update_layout(
            title=f"{product_name}<br>{category_name}",
            title_font_size=12,
            title_font_color='black',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='white',
            font=dict(color='black', size=10),
            height=250,
            xaxis_tickangle=0,
            margin=dict(l=10, r=10, t=50, b=10),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            )
        )
        return fig
    
    # 감정 분석 차트 표시
    if percentage_data:
        categories = list(percentage_data.keys())
        
        for i in range(0, len(categories), 3):
            cols = st.columns(3)
            for j, category in enumerate(categories[i:i+3]):
                with cols[j]:
                    if category in percentage_data:
                        chart = create_single_category_pie(percentage_data[category], category, '')
                        st.plotly_chart(chart, use_container_width=True)

    # 키워드 혼합 가중치 계싼
    def compute_mixed_weights(product_num, alpha=1.0, beta=1.0):
        try:
            conn = get_db_connection()
            
            # 상위 10개
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT customer_id, keyword, inserted_cnt
                    FROM tb_keyword_count_{product_num}
                    ORDER BY inserted_cnt DESC
                    LIMIT 10
                """)
                top10 = cur.fetchall()
            
            if not top10:
                return [], {}, {}, {}
            
            # 상위 9개
            top9 = top10[:9]
            top9_keywords = [kw for (_, kw, _) in top9]
            freq_map = {kw: cnt for (_, kw, cnt) in top9}
            max_cnt = max(freq_map.values()) if freq_map else 1

            # 키워드별 평균 별점 
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT ka.key_analysis, r.rates
                    FROM tb_key_analysis_{product_num} AS ka
                    LEFT JOIN tb_review_{product_num} AS r
                    ON r.customer_id = ka.customer_id
                    WHERE r.rates IS NOT NULL
                """)
                rows = cur.fetchall()

            # 키워드별 별점 합/개수 집계 : 9개
            rating_sum = {kw: 0.0 for kw in top9_keywords}
            rating_cnt = {kw: 0   for kw in top9_keywords}

            def to_float_0_5(x):
                try:
                    f = float(x)
                    return max(0.0, min(5.0, f))
                except:
                    return None

            for ka_str, rates in rows:
                try:
                    d = ast.literal_eval(ka_str) if isinstance(ka_str, str) else {}
                except Exception:
                    d = {}
                kw = d.get("키워드", None)
                if kw in rating_sum:
                    r = to_float_0_5(rates)
                    if r is not None:
                        rating_sum[kw] += r
                        rating_cnt[kw] += 1

            avg_rating = {kw: (round(rating_sum[kw]/rating_cnt[kw], 2) if rating_cnt[kw] > 0 else 0.0)
                        for kw in top9_keywords}

            # 계산 
            mixed_score = {}
            for kw in top9_keywords:
                # 빈도 비율
                freq_ratio = (freq_map[kw] / max_cnt) if max_cnt > 0 else 0
                # (평균별점/5)^alpha * (빈도비율)^beta * 5
                score = ((avg_rating[kw] / 5.0) ** alpha) * (freq_ratio ** beta) * 5.0
                mixed_score[kw] = round(score, 2)

            return top9_keywords, freq_map, avg_rating, mixed_score
        except Exception as e:
            return [], {}, {}, {}

    top9_keywords, freq_map, avg_rating, mixed_score = compute_mixed_weights(product_num=selected_product, alpha=1.0, beta=1.0)
    
    # 계산 표시
    if top9_keywords:
        groups = [top9_keywords[0:3], top9_keywords[3:6], top9_keywords[6:9]]
        titles = ["", "", ""]
        
        cols = st.columns(3)
        for idx, (group, title) in enumerate(zip(groups, titles)):
            with cols[idx]:
                if group:
                    y_vals = [mixed_score.get(k, 0) for k in group]
                    hover_texts = [
                        f"{k}{mixed_score.get(k,0):.2f} / 5"
                        f"<br>평균별점: {avg_rating.get(k,0):.2f} / 5"
                        f"<br>빈도: {freq_map.get(k,0)}"
                        for k in group
                    ]

                    fig = go.Figure(go.Bar(
                        x=group,
                        y=y_vals,
                        text=[f"{v:.2f}" for v in y_vals],
                        textposition="outside",
                        hovertext=hover_texts,
                        hoverinfo="text",
                        marker_color="rgba(227,123,179,0.70)"
                    ))
                    fig.update_layout(
                        title=title,
                        height=400,
                        xaxis_title="키워드",
                        yaxis_title="",
                        yaxis=dict(range=[0,5]),
                        margin=dict(l=10, r=10, t=35, b=10)
                    )
                    st.plotly_chart(fig, use_container_width=True)

    # 리뷰 요약 가져오기 
    @st.cache_data(ttl=300)
    def get_keyword_analysis(product_num):
        try:
            conn = get_db_connection()
            
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT customer_id, key_analysis
                    FROM tb_key_analysis_{product_num}
                """)
                results = cur.fetchall()
            summary_data = []
            for customer_id, key_analysis_str in results:
                try:
                    # 문자열로 저장된 딕셔너리를 파싱
                    analysis_data = ast.literal_eval(key_analysis_str)
                    
                    summary_data.append({
                        'customer_id': customer_id,
                        'keyword': analysis_data.get('키워드', ''),
                        'sentiment': analysis_data.get('감정', ''),
                        'summary': analysis_data.get('요약', '')
                    })
                except Exception as e:
                    continue
            return summary_data  
        except Exception as e:
            st.error(f"데이터 가져오기 실패: {e}")
            return []

    summary_data = get_keyword_analysis(selected_product)

    # 리뷰 데이터 가져오기
    def get_table_structure_and_reviews(product_num):
        try:
            # 가능한 리뷰 컬럼들 시도
            review_columns = ['contents', 'review', 'cleaned_review', 'CleanedReview', 'content', 'review_text', 'text']
            review_column = None
            
            with conn.cursor() as cur:
                for col_name in review_columns:
                    try:
                        cur.execute(f"SELECT `{col_name}` FROM tb_review_{product_num} LIMIT 1")
                        result = cur.fetchone()
                        if result:
                            review_column = col_name
                            break
                    except Exception as e:
                        continue
                
                if review_column:
                    # 리뷰 데이터 가져오기 
                    cur.execute(f"""
                        SELECT customer_id, `{review_column}`
                        FROM tb_review_{product_num}
                        WHERE `{review_column}` IS NOT NULL AND `{review_column}` != ''
                        LIMIT 10
                    """)
                    reviews = cur.fetchall()
                    return reviews, review_column
                else:
                    return [], None
                    
        except Exception as e:
            return [], None

    # 키워드와 리뷰 조합 데이터 가져오기
    def get_keyword_reviews(product_num, review_column):
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                    SELECT r.customer_id, r.`{review_column}`, ka.key_analysis
                    FROM tb_review_{product_num} r
                    INNER JOIN tb_key_analysis_{product_num} ka 
                    ON r.customer_id = ka.customer_id
                    WHERE r.`{review_column}` IS NOT NULL AND ka.key_analysis IS NOT NULL
                    LIMIT 15
                """)
                return cur.fetchall()
        except Exception as e:
            return []

    # 데이터 확인
    review_data, review_column = get_table_structure_and_reviews(selected_product)
    
    if review_data and review_column:
        # 키워드와 리뷰 조합 가져오기
        keyword_review_data = get_keyword_reviews(selected_product, review_column)
        
        if keyword_review_data:
            # 하이라이트 함수
            def highlight_text(text, keyword, sentiment):
                import html
                
                # 긍정/부정 관련 단어들
                positive_words = [
                    '좋', '만족', '추천', '최고', '완벽', '잘', '괜찮', '부드럽', '촉촉', '편하', 
                    '깨끗', '효과', '대박', '사랑', '마음에', '딱', '완전', '진짜', '정말', '너무', 
                    '엄청', '개', '굿', '예쁘', '훌륭', '뛰어나', '우수', '감동', '신기', '예쁘다'
                ]
                
                negative_words = [
                    '별로', '안좋', '실망', '아쉽', '나쁘', '불편', '어색', '끈적', '뻑뻑', '안','각질'
                ]
                
                # 감정에 따른 색상 설정
                if '긍정' in sentiment:
                    color = "#faa2d5"
                elif '부정' in sentiment:
                    color = "#badef2"
                else:
                    color = '#e0e0e0'
                
                # 하이라이트할 단어들 수집
                words_to_highlight = []
                
                # 키워드 추가
                if keyword in text:
                    words_to_highlight.append(keyword)
                
                # 감정 단어들 추가
                sentiment_words = positive_words if '긍정' in sentiment else negative_words
                for word in sentiment_words:
                    if word in text:
                        words_to_highlight.append(word)
                
                # 하이라이트 적용
                if words_to_highlight:
                    highlighted_text = html.escape(text)
                    
                    # 긴 단어부터 먼저 처리
                    words_to_highlight.sort(key=len, reverse=True)
                    
                    for word in words_to_highlight:
                        escaped_word = html.escape(word)
                        highlighted_word = f"<span style='background-color:{color}; color:#000; padding:2px 1px; border-radius:2px;'>{escaped_word}</span>"
                        highlighted_text = highlighted_text.replace(escaped_word, highlighted_word)
                    
                    return highlighted_text
                else:
                    return html.escape(text)
            
            # 감정별로 리뷰 분류
            positive_reviews = []
            negative_reviews = []
            neutral_reviews = []
            
            for customer_id, review_text, key_analysis_str in keyword_review_data:
                try:
                    analysis_data = ast.literal_eval(key_analysis_str)
                    sentiment = analysis_data.get('감정', '')
                    keyword = analysis_data.get('키워드', '')
                    
                    if '긍정' in sentiment:
                        positive_reviews.append({
                            'keyword': keyword,
                            'review': review_text,
                            'sentiment': sentiment
                        })
                    elif '부정' in sentiment:
                        negative_reviews.append({
                            'keyword': keyword,
                            'review': review_text,
                            'sentiment': sentiment
                        })
                    else:
                        neutral_reviews.append({
                            'keyword': keyword,
                            'review': review_text,
                            'sentiment': sentiment
                        })
                except Exception as e:
                    continue
            
            cols = st.columns(3)
            
            # 긍정 리뷰
            with cols[0]:
                st.subheader("긍정 리뷰")
                for i, review_data in enumerate(positive_reviews[:1]):
                    highlighted_text = highlight_text(
                        review_data['review'][:300] + ('...' if len(review_data['review']) > 300 else ''),
                        review_data['keyword'],
                        review_data['sentiment']
                    )
                    
                    st.markdown(f"{review_data['keyword']}")
                    st.markdown(highlighted_text, unsafe_allow_html=True)
                    
                
                if len(positive_reviews) == 0:
                    st.write("현재 페이지에 긍정 리뷰가 없습니다.")
            
            # 부정 리뷰
            with cols[1]:
                st.subheader("부정 리뷰")
                for i, review_data in enumerate(negative_reviews[:1]):
                    highlighted_text = highlight_text(
                        review_data['review'][:300] + ('...' if len(review_data['review']) > 300 else ''),
                        review_data['keyword'],
                        review_data['sentiment']
                    )
                    
                    st.markdown(f"{review_data['keyword']}")
                    st.markdown(highlighted_text, unsafe_allow_html=True)
                
                
                if len(negative_reviews) == 0:
                    st.write("현재 페이지에 부정 리뷰가 없습니다.")
            
            # 중립 리뷰
            with cols[2]:
                st.subheader("중립 리뷰")
                for i, review_data in enumerate(neutral_reviews[:1]):
                    highlighted_text = highlight_text(
                        review_data['review'][:300] + ('...' if len(review_data['review']) > 300 else ''),
                        review_data['keyword'],
                        review_data['sentiment']
                    )
                    
                    st.markdown(f"{review_data['keyword']}")
                    st.markdown(highlighted_text, unsafe_allow_html=True)
                
                
                if len(neutral_reviews) == 0:
                    st.write("중립 리뷰가 없습니다.")
        else:
            st.write("리뷰 데이터가 없습니다.")
    else:
        st.write("현재 페이지에 리뷰 데이터가 없습니다.")

#-----------------------컬럼3-----------------------------

with col3:
    # 키워드 상위 10개
    def get_top10_keywords(table_name, product_num):
        try:
            with conn.cursor() as cur:
                cur.execute(f"""
                SELECT customer_id, keyword, inserted_cnt 
                FROM {table_name} 
                ORDER BY inserted_cnt DESC 
                LIMIT 10
                """)
                results = cur.fetchall()
                return results
        except Exception as e:
            print(f"상위 10 키워드 에러 : {e}")
            return []
        finally:
            conn.close()
    # 선택된 상품의 키워드 데이터
    table_name = f'tb_keyword_count_{selected_product}'
    top10_results = get_top10_keywords(table_name, selected_product)
    if top10_results:
        keywords = [row[1] for row in top10_results]
        counts = [row[2] for row in top10_results]

        # 막대그래프
        fig = go.Figure(go.Bar(
            x=counts,
            y=keywords,
            marker_color="#FF3399",
            textposition='outside',
            orientation='h'
        ))

        fig.update_layout(
            height=800,
            margin=dict(t=80, b=10, l=10, r=10), 
            title=dict(
                text="리뷰 키워드 분석",
                x=0.5,
                xanchor='center',
                yanchor='top',
                font=dict(size=25)
            ),
            xaxis_title="언급량",
            yaxis_title="",
            yaxis={'categoryorder': 'total ascending'},
            font=dict(size=12)
        )

        fig.update_xaxes(tickangle=45)
        fig.update_xaxes(visible=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.subheader("리뷰 키워드 분석")
        st.write("키워드 데이터가 없습니다.")