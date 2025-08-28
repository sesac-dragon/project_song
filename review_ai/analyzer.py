import os
import json
import requests
import time
import html
import ast
from collections import Counter
import pymysql

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

#상품 이름 가져오기 - 사이드바
def get_product_list():
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

#상품 정보 가져오기
def get_product_detail(selected_product):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, shop_name, name, original_price, discount_price, original_image
                FROM tb_product_{selected_product}
                ORDER BY id DESC LIMIT 1
            """)
            result = cur.fetchone()
            
            if result:
                return {
                    'product_num': selected_product,
                    'id': result[0],
                    'shop_name': result[1], 
                    'name': result[2],
                    'original_price': result[3],
                    'discount_price': result[4],
                    'image': result[5]
                }
    except Exception as e:
        print(f"제품 정보 가져오기 오류: {e}")
    finally:
        conn.close()
    return None

#별점
def get_rating_data(product_num):
    conn = get_db_connection()
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
            return avg_rating, len(ratings)
    except Exception as e:
        print(f"평점 데이터 오류: {e}")
    finally:
        conn.close()
    return 0.0, 0

#카테고리 감정분석
def get_sentiment_data(product_num):
    conn = get_db_connection()
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
        print(f"감정 데이터 오류: {e}")
    finally:
        conn.close()
    return {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0}

#키워드 감정분석
def get_emotion_data(product_num):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT emo_analysis FROM tb_emotion_{product_num}")
            rows = cur.fetchall()
        
        cate_counter = Counter()
        total_cate = 0
        
        for (emo_str,) in rows:
            try:
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
        print(f"감정 카테고리 데이터 오류: {e}")
    finally:
        conn.close()
    return {}, Counter()

#키워드 계산
def compute_mixed_weights(product_num, alpha=1.0, beta=1.0):
    conn = get_db_connection()
    try:
        # Top10 키워드 가져오기
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

        # 키워드별 별점 합/개수 집계
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

        # 혼합 점수 계산 
        mixed_score = {}
        for kw in top9_keywords:
            freq_ratio = (freq_map[kw] / max_cnt) if max_cnt > 0 else 0
            score = ((avg_rating[kw] / 5.0) ** alpha) * (freq_ratio ** beta) * 5.0
            mixed_score[kw] = round(score, 2)

        return top9_keywords, freq_map, avg_rating, mixed_score
    except Exception as e:
        print(f"혼합 가중치 계산 오류: {e}")
    finally:
        conn.close()
    return [], {}, {}, {}

#키워드 분석 
def get_keyword_analysis(product_num):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT customer_id, key_analysis
                FROM tb_key_analysis_{product_num}
            """)
            results = cur.fetchall()
        
        summary_data = []
        for customer_id, key_analysis_str in results:
            try:
                analysis_data = ast.literal_eval(key_analysis_str)
                summary_data.append({
                    'customer_id': customer_id,
                    'keyword': analysis_data.get('키워드', ''),
                    'sentiment': analysis_data.get('감정', ''),
                    'summary': analysis_data.get('요약', '')
                })
            except Exception:
                continue
        return summary_data  
    except Exception as e:
        print(f"키워드 분석 데이터 오류: {e}")
    finally:
        conn.close()
    return []

#리뷰가져오기(감정분석하이라이트용)
def get_table_structure_and_reviews(product_num):
    conn = get_db_connection()
    try:
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
                except Exception:
                    continue
            
            if review_column:
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
        print(f"리뷰 데이터 오류: {e}")
    finally:
        conn.close()
    return [], None

#키워드-리뷰 가져오기
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
        print(f"키워드-리뷰 조합 데이터 오류: {e}")
    finally:
        conn.close()
    return []

#언급 상위 키워드 10개
def get_top10_keywords(product_num):
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
            SELECT customer_id, keyword, inserted_cnt 
            FROM tb_keyword_count_{product_num} 
            ORDER BY inserted_cnt DESC 
            LIMIT 10
            """)
            results = cur.fetchall()
            return results
    except Exception as e:
        print(f"상위 10 키워드 에러: {e}")
    finally:
        conn.close()
    return []

#리뷰 하이라이트 긍/부정
def highlight_text(text, keyword, sentiment):
    # 긍정/부정 관련 단어들
    positive_words = [
        '좋', '만족', '추천', '최고', '완벽', '잘', '괜찮', '부드럽', '촉촉', '편하', 
        '깨끗', '효과', '대박', '사랑', '마음에', '등', '완전', '진짜', '정말', '너무', 
        '엄청', '개', '굿', '예쁘', '훌륭', '뛰어나', '우수', '감동', '신기', '예쁘다'
    ]
    
    negative_words = [
        '별로', '안좋', '실망', '아쉽', '나쁜', '불편', '어색', '눅눅', '뻑뻑', '안','감질'
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