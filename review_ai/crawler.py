
import os
import json
import requests
import time
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# OPEN AI API 키 설정
load_dotenv()

MY_API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=MY_API_KEY)

#상품 1
def crawling_1():
    url = "https://api.zigzag.kr/api/2/graphql/batch/GetNormalReviewFeedList"

    payload = [
        {
            "operationName": "GetNormalReviewFeedList",
            "variables": {
                "order": "BEST_SCORE_DESC",
                "limit_count": 100,
                "product_id": "149419525",
                "skip_count": 0
            },
            "query": """query GetNormalReviewFeedList($product_id: ID!, $limit_count: Int, $skip_count: Int, $order: UxReviewListOrderType) {
    feed_list: ux_review_list(
        input: {product_id: $product_id, order: $order, pagination: {limit_count: $limit_count, skip_count: $skip_count}}
    ) {
        ...ReviewFeedListOnFeed
        __typename
    }
    }

    fragment ReviewFeedListOnFeed on UxReviewList {
    total_count
    item_list {
        ...UxReviewFeedItemOnFeed
        __typename
    }
    __typename
    }

    fragment UxReviewFeedItemOnFeed on UxReview {
    id
    shop_id
    product_id
    type
    fulfillment_badge {
        type
        text
        image_url
        image_size {
        width
        height
        __typename
        }
        small_image_size {
        width
        height
        __typename
        }
        __typename
    }
    status
    contents
    date_created
    date_updated
    rating
    user_account_id
    like_list {
        type
        count
        __typename
    }
    display_limited
    updatable
    additional_description
    country
    order_item_number
    site_id
    user_reply_count
    reply_list {
        contents
        __typename
    }
    requested_user {
        is_mine
        liked_list
        is_abuse_reported
        __typename
    }
    attachment_list {
        product_review_id
        original_url
        thumbnail_url
        status
        __typename
    }
    attribute_list {
        question {
        label
        value
        category
        __typename
        }
        answer {
        label
        value
        __typename
        }
        __typename
    }
    reviewer {
        body_text
        reviewer_id
        profile {
        nickname
        masked_email
        profile_image_url
        is_ranker
        is_visible
        badge {
            ... on UxIconTextBadgeComponent {
            text {
                text
                __typename
            }
            __typename
            }
            __typename
        }
        __typename
        }
        __typename
    }
    product_info {
        pdp_landing_url
        browsing_type
        image_url
        name
        option_detail_list {
        name
        value
        __typename
        }
        __typename
    }
    seller_event_reward_info {
        badge {
        text {
            text
            __typename
        }
        __typename
        }
        __typename
    }
    __typename
    }"""
        }
    ]

    headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
            'Origin': 'https://zigzag.kr',
            "Referer": "https://zigzag.kr/"
    }
    res = requests.post(url, json=payload, headers=headers)
    time.sleep(2)

    if res.status_code == 200:
        data = res.json()
    else:
        print(res.status_code, res.text)
        return None

    try:
        review_list1 = []
        reviews = data[0]['data']['feed_list']['item_list']

        for review in reviews :    

            questions=[]
            answers=[]
            
            customer_id= review.get('id', '')
            product_name = reviews[0]['product_info']['name']        
            date_created =review.get('date_created', '')
            rates=review.get('rating','')
            contents= review.get('contents', '')        
            dates= datetime.fromtimestamp(int(date_created)/1000).strftime('%Y-%m-%d')

            for attr in review.get('attribute_list',[]):
                questions.append(attr['question']['label'])
                answers.append(attr['answer']['label'])

            question = "\n".join(map(str, questions))
            answer = "\n".join(map(str, answers))
            review_list1.append((
                customer_id,
                product_name,
                dates,
                rates,
                contents,
                question,
                answer))
        return review_list1
        
    except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"상품1 리뷰 크롤링 중 에러 ! : {e}")
            return None

#상품 2

def crawling_2():
    url = "https://api.zigzag.kr/api/2/graphql/batch/GetNormalReviewFeedList"

    payload = [
        {
            "operationName": "GetNormalReviewFeedList",
            "variables": {
                "order": "BEST_SCORE_DESC",
                "limit_count": 100,
                "product_id": "162970992",
                "skip_count": 0
            },
            "query": """query GetNormalReviewFeedList($product_id: ID!, $limit_count: Int, $skip_count: Int, $order: UxReviewListOrderType) {
        feed_list: ux_review_list(
        input: {product_id: $product_id, order: $order, pagination: {limit_count: $limit_count, skip_count: $skip_count}}
        ) {
        ...ReviewFeedListOnFeed
        __typename
        }
    }

    fragment ReviewFeedListOnFeed on UxReviewList {
        total_count
        item_list {
        ...UxReviewFeedItemOnFeed
        __typename
        }
        __typename
    }

    fragment UxReviewFeedItemOnFeed on UxReview {
        id
        shop_id
        product_id
        type
        fulfillment_badge {
        type
        text
        image_url
        image_size {
            width
            height
            __typename
        }
        small_image_size {
            width
            height
            __typename
        }
        __typename
        }
        status
        contents
        date_created
        date_updated
        rating
        user_account_id
        like_list {
        type
        count
        __typename
        }
        display_limited
        updatable
        additional_description
        country
        order_item_number
        site_id
        user_reply_count
        reply_list {
        contents
        __typename
        }
        requested_user {
        is_mine
        liked_list
        is_abuse_reported
        __typename
        }
        attachment_list {
        product_review_id
        original_url
        thumbnail_url
        status
        __typename
        }
        attribute_list {
        question {
            label
            value
            category
            __typename
        }
        answer {
            label
            value
            __typename
        }
        __typename
        }
        reviewer {
        body_text
        reviewer_id
        profile {
            nickname
            masked_email
            profile_image_url
            is_ranker
            is_visible
            badge {
            ... on UxIconTextBadgeComponent {
                text {
                text
                __typename
                }
                __typename
            }
            __typename
            }
            __typename
        }
        __typename
        }
        product_info {
        pdp_landing_url
        browsing_type
        image_url
        name
        option_detail_list {
            name
            value
            __typename
        }
        __typename
        }
        seller_event_reward_info {
        badge {
            text {
            text
            __typename
            }
            __typename
        }
        __typename
        }
        __typename
    }"""
        }
    ]

    headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
            'Origin': 'https://zigzag.kr',
            "Referer": "https://zigzag.kr/"
    }

    res = requests.post(url, json=payload, headers=headers)
    time.sleep(2)

    if res.status_code == 200:
        data = res.json()
    else:
        print(res.status_code, res.text)
        return None
    try:
        review_list2 = []
        reviews = data[0]['data']['feed_list']['item_list']

        for review in reviews :    

            questions=[]
            answers=[]
            
            customer_id= review.get('id', '')
            product_name = reviews[0]['product_info']['name']        
            date_created =review.get('date_created', '')
            rates=review.get('rating','')
            contents= review.get('contents', '')        
            dates= datetime.fromtimestamp(int(date_created)/1000).strftime('%Y-%m-%d')

            for attr in review.get('attribute_list',[]):
                questions.append(attr['question']['label'])
                answers.append(attr['answer']['label'])

            question = "\n".join(map(str, questions))
            answer = "\n".join(map(str, answers))
            review_list2.append((
                customer_id,
                product_name,
                dates,
                rates,
                contents,
                question,
                answer))
        return review_list2
    except Exception as e:
          import traceback
          traceback.print_exc()
          print(f"상품2 리뷰 크롤링 중 에러 ! : {e}")
          return None

#상품3

def crawling_3():
    url = "https://api.zigzag.kr/api/2/graphql/batch/GetNormalReviewFeedList"

    payload = [
        {
            "operationName": "GetNormalReviewFeedList",
            "variables": {
                "order": "BEST_SCORE_DESC",
                "limit_count": 100,
                "product_id": "131281148",
                "skip_count": 0
            },
            "query": """query GetNormalReviewFeedList($product_id: ID!, $limit_count: Int, $skip_count: Int, $order: UxReviewListOrderType) {
        feed_list: ux_review_list(
        input: {product_id: $product_id, order: $order, pagination: {limit_count: $limit_count, skip_count: $skip_count}}
        ) {
        ...ReviewFeedListOnFeed
        __typename
        }
    }

    fragment ReviewFeedListOnFeed on UxReviewList {
        total_count
        item_list {
        ...UxReviewFeedItemOnFeed
        __typename
        }
        __typename
    }

    fragment UxReviewFeedItemOnFeed on UxReview {
        id
        shop_id
        product_id
        type
        fulfillment_badge {
        type
        text
        image_url
        image_size {
            width
            height
            __typename
        }
        small_image_size {
            width
            height
            __typename
        }
        __typename
        }
        status
        contents
        date_created
        date_updated
        rating
        user_account_id
        like_list {
        type
        count
        __typename
        }
        display_limited
        updatable
        additional_description
        country
        order_item_number
        site_id
        user_reply_count
        reply_list {
        contents
        __typename
        }
        requested_user {
        is_mine
        liked_list
        is_abuse_reported
        __typename
        }
        attachment_list {
        product_review_id
        original_url
        thumbnail_url
        status
        __typename
        }
        attribute_list {
        question {
            label
            value
            category
            __typename
        }
        answer {
            label
            value
            __typename
        }
        __typename
        }
        reviewer {
        body_text
        reviewer_id
        profile {
            nickname
            masked_email
            profile_image_url
            is_ranker
            is_visible
            badge {
            ... on UxIconTextBadgeComponent {
                text {
                text
                __typename
                }
                __typename
            }
            __typename
            }
            __typename
        }
        __typename
        }
        product_info {
        pdp_landing_url
        browsing_type
        image_url
        name
        option_detail_list {
            name
            value
            __typename
        }
        __typename
        }
        seller_event_reward_info {
        badge {
            text {
            text
            __typename
            }
            __typename
        }
        __typename
        }
        __typename
    }"""
        }
    ]

    headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
            'Origin': 'https://zigzag.kr',
            "Referer": "https://zigzag.kr/"
    }
    res = requests.post(url, json=payload, headers=headers)
    time.sleep(2)

    if res.status_code == 200:
        data = res.json()
    else:
        print(res.status_code, res.text)
        return None

    try:
        review_list3 = []
        reviews = data[0]['data']['feed_list']['item_list']

        for review in reviews :    

            questions=[]
            answers=[]
            
            customer_id= review.get('id', '')
            product_name = reviews[0]['product_info']['name']        
            date_created =review.get('date_created', '')
            rates=review.get('rating','')
            contents= review.get('contents', '')        
            dates= datetime.fromtimestamp(int(date_created)/1000).strftime('%Y-%m-%d')

            for attr in review.get('attribute_list',[]):
                questions.append(attr['question']['label'])
                answers.append(attr['answer']['label'])

            question = "\n".join(map(str, questions))
            answer = "\n".join(map(str, answers))
            review_list3.append((
                customer_id,
                product_name,
                dates,
                rates,
                contents,
                question,
                answer))
            return review_list3
    except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"상품3 리뷰 크롤링 중 에러 ! : {e}")
            return None

#상품 1. 상품정보 크롤링
def product_info_1():
    url = "https://api.zigzag.kr/api/2/graphql"

    # headers 정의 추가
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
        'Origin': 'https://zigzag.kr',
        'Referer': 'https://zigzag.kr/'
    }

    query = """
            fragment OptionItemList on PdpCatalogItem { 
                id name price price_delta final_price item_code sales_status display_status remain_stock 
                is_zigzin delivery_type expected_delivery_date expected_delivery_time 
                discount_info { image_url title color order } 
                item_attribute_list { id name value value_id } 
                wms_notification_info { active } 
            } 
            
            query GetCatalogProductDetailPageOption($catalog_product_id: ID!, $input: PdpBaseInfoInput) { 
                pdp_option_info(catalog_product_id: $catalog_product_id, input: $input) { 
                    catalog_product { 
                        shop_id shop_name shop_main_domain id name fulfillment_type external_code 
                        minimum_order_quantity maximum_order_quantity coupon_available_status 
                        scheduled_sale_date 
                        discount_info { image_url title color } 
                        estimated_shipping_date { estimate_list { day probability } } 
                        shipping_fee { fee_type base_fee minimum_free_shipping_fee } 
                        shipping_company { return_company } 
                        managed_category_list { id category_id value key depth } 
                        meta_catalog_product_info { id is_able_to_buy pdp_url browsing_type } 
                        product_price { 
                            first_order_discount { 
                                price promotion_id discount_type discount_amount discount_rate_bp min_required_amount 
                            } 
                            coupon_discount_info_list { 
                                target_type discount_type discount_amount discount_rate_bp 
                                discount_amount_of_amount_coupon min_required_amount max_discount_amount 
                            } 
                            display_final_price { 
                                final_price { 
                                    badge { text color { normal } } 
                                    color { normal } 
                                } 
                                final_price_additional { 
                                    badge { text } 
                                    color { normal } 
                                } 
                            } 
                            product_promotion_discount_info { discount_amount } 
                            max_price_info { price } 
                            final_discount_info { discount_price } 
                        } 
                        trait_list { type } 
                        promotion_info { 
                            bogo_required_quantity promotion_id promotion_type 
                            bogo_info { 
                                required_quantity discount_type discount_amount discount_rate_bp 
                            } 
                        } 
                        product_image_list { url origin_url pdp_thumbnail_url pdp_static_image_url image_type } 
                        product_option_list { 
                            id order name code required option_type 
                            value_list { id code value static_url jpeg_url } 
                        } 
                        matching_catalog_product_info { 
                            id name is_able_to_buy pdp_url fulfillment_type browsing_type external_code 
                            product_price { 
                                max_price_info { price color { normal } badge { text color { normal } } } 
                                final_discount_info { discount_price } 
                            } 
                            discount_info { color title image_url order } 
                            shipping_fee { fee_type base_fee minimum_free_shipping_fee } 
                            option_list { 
                                id order name code required option_type 
                                value_list { id code value static_url jpeg_url } 
                            } 
                        } 
                        product_additional_option_list { 
                            id order name code required option_type 
                            value_list { id code value static_url jpeg_url } 
                        } 
                        additional_item_list { 
                            id name price price_delta item_code sales_status display_status option_type 
                            is_zigzin delivery_type expected_delivery_date 
                            item_attribute_list { id name value value_id } 
                            wms_notification_info { active } 
                        } 
                        custom_input_option_list { name is_required: required max_length } 
                        matched_item_list { ...OptionItemList } 
                        zigzin_item_list { ...OptionItemList } 
                        is_only_zigzin_button_visible 
                        color_image_list { is_main image_url image_width image_height webp_image_url color_list } 
                        store_deal_banner { title guide_text } 
                        category_list { category_id value } 
                        shipping_fee { fee_type base_fee minimum_free_shipping_fee additional_shipping_fee_text } 
                        minimum_order_quantity_type 
                    } 
                    flags { is_purchase_only_one_at_time is_cart_button_visible } 
                    key_color { 
                        buy_button { 
                            text { disabled enabled } 
                            background { disabled enabled } 
                        } 
                        discount_info_of_atf 
                    } 
                } 
            }"""

    variables = {
        "catalog_product_id": "149419525",
        "input": {
            "catalog_product_id": "149419525", 
            "entry_source_type": ""
        }
    }
            
    payload = {
        "query": query,
        "variables": variables,
        "operationName": "GetCatalogProductDetailPageOption"
    }

    res = requests.post(url, json=payload, headers=headers)
    time.sleep(2)

    if res.status_code == 200:
        data = res.json()
    else:
        print("에러:", res.status_code)

    product_list_1=[]
    try:
        pdp_info = data['data']['pdp_option_info']
        catalog_product = pdp_info.get('catalog_product', '')
        #상품id
        id = catalog_product.get('id', '')
        # 상품명
        name = catalog_product.get('name', '')
        # 브랜드명
        shop_name = catalog_product.get('shop_name', '') 
        # 가격
        product_price = catalog_product.get('product_price', '')
        final_discount_info = product_price.get('final_discount_info', '')
        # 할인가 정보
        discount_price = final_discount_info.get('discount_price', '')
        #원가 정보
        max_price_info = product_price.get('max_price_info', '')
        original_price = max_price_info.get('price', '')
        
        # 이미지 추출
        product_images = catalog_product.get('product_image_list', '')

        main_images = []
        for img in product_images:
            image_type = img.get('image_type')
            if image_type == 'main':
                main_images.append(img)
        if main_images:
            original_image = main_images[0].get('origin_url', '') or main_images[0].get('url', '')
        elif product_images:
            original_image = product_images[0].get('origin_url', '') or product_images[0].get('url', '')
            
        product_list_1.append(id)
        product_list_1.append(shop_name)
        product_list_1.append(name)
        product_list_1.append(original_price)
        product_list_1.append(discount_price)
        product_list_1.append(original_image)
        return product_list_1
    
    except Exception as e:
        print(f"상품 정보 추출 중 에러 ! : {e}")
        return []


#상품 2. 상품정보 크롤링
def product_info_():
    url = "https://api.zigzag.kr/api/2/graphql/batch/GetNormalReviewFeedList"

    payload = [
        {
            "operationName": "GetNormalReviewFeedList",
            "variables": {
                "order": "BEST_SCORE_DESC",
                "limit_count": 100,
                "product_id": "131281148",
                "skip_count": 0
            },
            "query": """query GetNormalReviewFeedList($product_id: ID!, $limit_count: Int, $skip_count: Int, $order: UxReviewListOrderType) {
        feed_list: ux_review_list(
        input: {product_id: $product_id, order: $order, pagination: {limit_count: $limit_count, skip_count: $skip_count}}
        ) {
        ...ReviewFeedListOnFeed
        __typename
        }
    }

    fragment ReviewFeedListOnFeed on UxReviewList {
        total_count
        item_list {
        ...UxReviewFeedItemOnFeed
        __typename
        }
        __typename
    }

    fragment UxReviewFeedItemOnFeed on UxReview {
        id
        shop_id
        product_id
        type
        fulfillment_badge {
        type
        text
        image_url
        image_size {
            width
            height
            __typename
        }
        small_image_size {
            width
            height
            __typename
        }
        __typename
        }
        status
        contents
        date_created
        date_updated
        rating
        user_account_id
        like_list {
        type
        count
        __typename
        }
        display_limited
        updatable
        additional_description
        country
        order_item_number
        site_id
        user_reply_count
        reply_list {
        contents
        __typename
        }
        requested_user {
        is_mine
        liked_list
        is_abuse_reported
        __typename
        }
        attachment_list {
        product_review_id
        original_url
        thumbnail_url
        status
        __typename
        }
        attribute_list {
        question {
            label
            value
            category
            __typename
        }
        answer {
            label
            value
            __typename
        }
        __typename
        }
        reviewer {
        body_text
        reviewer_id
        profile {
            nickname
            masked_email
            profile_image_url
            is_ranker
            is_visible
            badge {
            ... on UxIconTextBadgeComponent {
                text {
                text
                __typename
                }
                __typename
            }
            __typename
            }
            __typename
        }
        __typename
        }
        product_info {
        pdp_landing_url
        browsing_type
        image_url
        name
        option_detail_list {
            name
            value
            __typename
        }
        __typename
        }
        seller_event_reward_info {
        badge {
            text {
            text
            __typename
            }
            __typename
        }
        __typename
        }
        __typename
    }"""
        }
    ]

    headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15',
            'Origin': 'https://zigzag.kr',
            "Referer": "https://zigzag.kr/"
    }
    res = requests.post(url, json=payload, headers=headers)
    time.sleep(2)

    if res.status_code == 200:
        data = res.json()
    else:
        print(res.status_code, res.text)
        return None

    try:
        review_list3 = []
        reviews = data[0]['data']['feed_list']['item_list']

        for review in reviews :    

            questions=[]
            answers=[]
            
            customer_id= review.get('id', '')
            product_name = reviews[0]['product_info']['name']        
            date_created =review.get('date_created', '')
            rates=review.get('rating','')
            contents= review.get('contents', '')        
            dates= datetime.fromtimestamp(int(date_created)/1000).strftime('%Y-%m-%d')

            for attr in review.get('attribute_list',[]):
                questions.append(attr['question']['label'])
                answers.append(attr['answer']['label'])

            question = "\n".join(map(str, questions))
            answer = "\n".join(map(str, answers))
            review_list3.append((
                customer_id,
                product_name,
                dates,
                rates,
                contents,
                question,
                answer))
            return review_list3
    except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"상품3 리뷰 크롤링 중 에러 ! : {e}")
            return None

#상품 2. 상품정보 크롤링
def product_info_2():
    url = "https://api.zigzag.kr/api/2/graphql"

    # headers 정의 추가
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
        'Origin': 'https://zigzag.kr',
        'Referer': 'https://zigzag.kr/'
    }

    query = """
            fragment OptionItemList on PdpCatalogItem { 
                id name price price_delta final_price item_code sales_status display_status remain_stock 
                is_zigzin delivery_type expected_delivery_date expected_delivery_time 
                discount_info { image_url title color order } 
                item_attribute_list { id name value value_id } 
                wms_notification_info { active } 
            } 
            
            query GetCatalogProductDetailPageOption($catalog_product_id: ID!, $input: PdpBaseInfoInput) { 
                pdp_option_info(catalog_product_id: $catalog_product_id, input: $input) { 
                    catalog_product { 
                        shop_id shop_name shop_main_domain id name fulfillment_type external_code 
                        minimum_order_quantity maximum_order_quantity coupon_available_status 
                        scheduled_sale_date 
                        discount_info { image_url title color } 
                        estimated_shipping_date { estimate_list { day probability } } 
                        shipping_fee { fee_type base_fee minimum_free_shipping_fee } 
                        shipping_company { return_company } 
                        managed_category_list { id category_id value key depth } 
                        meta_catalog_product_info { id is_able_to_buy pdp_url browsing_type } 
                        product_price { 
                            first_order_discount { 
                                price promotion_id discount_type discount_amount discount_rate_bp min_required_amount 
                            } 
                            coupon_discount_info_list { 
                                target_type discount_type discount_amount discount_rate_bp 
                                discount_amount_of_amount_coupon min_required_amount max_discount_amount 
                            } 
                            display_final_price { 
                                final_price { 
                                    badge { text color { normal } } 
                                    color { normal } 
                                } 
                                final_price_additional { 
                                    badge { text } 
                                    color { normal } 
                                } 
                            } 
                            product_promotion_discount_info { discount_amount } 
                            max_price_info { price } 
                            final_discount_info { discount_price } 
                        } 
                        trait_list { type } 
                        promotion_info { 
                            bogo_required_quantity promotion_id promotion_type 
                            bogo_info { 
                                required_quantity discount_type discount_amount discount_rate_bp 
                            } 
                        } 
                        product_image_list { url origin_url pdp_thumbnail_url pdp_static_image_url image_type } 
                        product_option_list { 
                            id order name code required option_type 
                            value_list { id code value static_url jpeg_url } 
                        } 
                        matching_catalog_product_info { 
                            id name is_able_to_buy pdp_url fulfillment_type browsing_type external_code 
                            product_price { 
                                max_price_info { price color { normal } badge { text color { normal } } } 
                                final_discount_info { discount_price } 
                            } 
                            discount_info { color title image_url order } 
                            shipping_fee { fee_type base_fee minimum_free_shipping_fee } 
                            option_list { 
                                id order name code required option_type 
                                value_list { id code value static_url jpeg_url } 
                            } 
                        } 
                        product_additional_option_list { 
                            id order name code required option_type 
                            value_list { id code value static_url jpeg_url } 
                        } 
                        additional_item_list { 
                            id name price price_delta item_code sales_status display_status option_type 
                            is_zigzin delivery_type expected_delivery_date 
                            item_attribute_list { id name value value_id } 
                            wms_notification_info { active } 
                        } 
                        custom_input_option_list { name is_required: required max_length } 
                        matched_item_list { ...OptionItemList } 
                        zigzin_item_list { ...OptionItemList } 
                        is_only_zigzin_button_visible 
                        color_image_list { is_main image_url image_width image_height webp_image_url color_list } 
                        store_deal_banner { title guide_text } 
                        category_list { category_id value } 
                        shipping_fee { fee_type base_fee minimum_free_shipping_fee additional_shipping_fee_text } 
                        minimum_order_quantity_type 
                    } 
                    flags { is_purchase_only_one_at_time is_cart_button_visible } 
                    key_color { 
                        buy_button { 
                            text { disabled enabled } 
                            background { disabled enabled } 
                        } 
                        discount_info_of_atf 
                    } 
                } 
            }"""

    variables = {
        "catalog_product_id": "162970992",
        "input": {
            "catalog_product_id": "162970992",
            "entry_source_type": ""
        }
    }
            
    payload = {
        "query": query,
        "variables": variables,
        "operationName": "GetCatalogProductDetailPageOption"
    }

    res = requests.post(url, json=payload, headers=headers)
    time.sleep(2)

    if res.status_code == 200:
        data = res.json()
    else:
        print("에러:", res.status_code)

    product_list_2=[]
    try:
        pdp_info = data['data']['pdp_option_info']
        catalog_product = pdp_info.get('catalog_product', '')
        #상품id
        id = catalog_product.get('id', '')
        # 상품명
        name = catalog_product.get('name', '')
        # 브랜드명
        shop_name = catalog_product.get('shop_name', '') 
        # 가격
        product_price = catalog_product.get('product_price', '')
        final_discount_info = product_price.get('final_discount_info', '')
        # 할인가 정보
        discount_price = final_discount_info.get('discount_price', '')
        #원가 정보
        max_price_info = product_price.get('max_price_info', '')
        original_price = max_price_info.get('price', '')
        
        # 이미지 추출
        product_images = catalog_product.get('product_image_list', '')

        main_images = []
        for img in product_images:
            image_type = img.get('image_type')
            if image_type == 'main':
                main_images.append(img)
        if main_images:
            original_image = main_images[0].get('origin_url', '') or main_images[0].get('url', '')
        elif product_images:
            original_image = product_images[0].get('origin_url', '') or product_images[0].get('url', '')
            
        product_list_2.append(id)
        product_list_2.append(shop_name)
        product_list_2.append(name)
        product_list_2.append(original_price)
        product_list_2.append(discount_price)
        product_list_2.append(original_image)
        return product_list_2
    
    except Exception as e:
        print(f"상품 정보 추출 중 에러 ! : {e}")
        return []


#상품 3. 상품정보 크롤링
def product_info_3():
    url = "https://api.zigzag.kr/api/2/graphql"

    # headers 정의 추가
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1',
        'Origin': 'https://zigzag.kr',
        'Referer': 'https://zigzag.kr/'
    }

    query = """
            fragment OptionItemList on PdpCatalogItem { 
                id name price price_delta final_price item_code sales_status display_status remain_stock 
                is_zigzin delivery_type expected_delivery_date expected_delivery_time 
                discount_info { image_url title color order } 
                item_attribute_list { id name value value_id } 
                wms_notification_info { active } 
            } 
            
            query GetCatalogProductDetailPageOption($catalog_product_id: ID!, $input: PdpBaseInfoInput) { 
                pdp_option_info(catalog_product_id: $catalog_product_id, input: $input) { 
                    catalog_product { 
                        shop_id shop_name shop_main_domain id name fulfillment_type external_code 
                        minimum_order_quantity maximum_order_quantity coupon_available_status 
                        scheduled_sale_date 
                        discount_info { image_url title color } 
                        estimated_shipping_date { estimate_list { day probability } } 
                        shipping_fee { fee_type base_fee minimum_free_shipping_fee } 
                        shipping_company { return_company } 
                        managed_category_list { id category_id value key depth } 
                        meta_catalog_product_info { id is_able_to_buy pdp_url browsing_type } 
                        product_price { 
                            first_order_discount { 
                                price promotion_id discount_type discount_amount discount_rate_bp min_required_amount 
                            } 
                            coupon_discount_info_list { 
                                target_type discount_type discount_amount discount_rate_bp 
                                discount_amount_of_amount_coupon min_required_amount max_discount_amount 
                            } 
                            display_final_price { 
                                final_price { 
                                    badge { text color { normal } } 
                                    color { normal } 
                                } 
                                final_price_additional { 
                                    badge { text } 
                                    color { normal } 
                                } 
                            } 
                            product_promotion_discount_info { discount_amount } 
                            max_price_info { price } 
                            final_discount_info { discount_price } 
                        } 
                        trait_list { type } 
                        promotion_info { 
                            bogo_required_quantity promotion_id promotion_type 
                            bogo_info { 
                                required_quantity discount_type discount_amount discount_rate_bp 
                            } 
                        } 
                        product_image_list { url origin_url pdp_thumbnail_url pdp_static_image_url image_type } 
                        product_option_list { 
                            id order name code required option_type 
                            value_list { id code value static_url jpeg_url } 
                        } 
                        matching_catalog_product_info { 
                            id name is_able_to_buy pdp_url fulfillment_type browsing_type external_code 
                            product_price { 
                                max_price_info { price color { normal } badge { text color { normal } } } 
                                final_discount_info { discount_price } 
                            } 
                            discount_info { color title image_url order } 
                            shipping_fee { fee_type base_fee minimum_free_shipping_fee } 
                            option_list { 
                                id order name code required option_type 
                                value_list { id code value static_url jpeg_url } 
                            } 
                        } 
                        product_additional_option_list { 
                            id order name code required option_type 
                            value_list { id code value static_url jpeg_url } 
                        } 
                        additional_item_list { 
                            id name price price_delta item_code sales_status display_status option_type 
                            is_zigzin delivery_type expected_delivery_date 
                            item_attribute_list { id name value value_id } 
                            wms_notification_info { active } 
                        } 
                        custom_input_option_list { name is_required: required max_length } 
                        matched_item_list { ...OptionItemList } 
                        zigzin_item_list { ...OptionItemList } 
                        is_only_zigzin_button_visible 
                        color_image_list { is_main image_url image_width image_height webp_image_url color_list } 
                        store_deal_banner { title guide_text } 
                        category_list { category_id value } 
                        shipping_fee { fee_type base_fee minimum_free_shipping_fee additional_shipping_fee_text } 
                        minimum_order_quantity_type 
                    } 
                    flags { is_purchase_only_one_at_time is_cart_button_visible } 
                    key_color { 
                        buy_button { 
                            text { disabled enabled } 
                            background { disabled enabled } 
                        } 
                        discount_info_of_atf 
                    } 
                } 
            }"""

    variables = {
        "catalog_product_id": "131281148",
        "input": {
            "catalog_product_id": "131281148",
            "entry_source_type": ""
        }
    }
            
    payload = {
        "query": query,
        "variables": variables,
        "operationName": "GetCatalogProductDetailPageOption"
    }

    res = requests.post(url, json=payload, headers=headers)
    time.sleep(2)

    if res.status_code == 200:
        data = res.json()
    else:
        print("에러:", res.status_code)

    product_list_3=[]
    try:
        pdp_info = data['data']['pdp_option_info']
        catalog_product = pdp_info.get('catalog_product', '')
        #상품id
        id = catalog_product.get('id', '')
        # 상품명
        name = catalog_product.get('name', '')
        # 브랜드명
        shop_name = catalog_product.get('shop_name', '') 
        # 가격
        product_price = catalog_product.get('product_price', '')
        final_discount_info = product_price.get('final_discount_info', '')
        # 할인가 정보
        discount_price = final_discount_info.get('discount_price', '')
        #원가 정보
        max_price_info = product_price.get('max_price_info', '')
        original_price = max_price_info.get('price', '')
        
        # 이미지 추출
        product_images = catalog_product.get('product_image_list', '')

        main_images = []
        for img in product_images:
            image_type = img.get('image_type')
            if image_type == 'main':
                main_images.append(img)
        if main_images:
            original_image = main_images[0].get('origin_url', '') or main_images[0].get('url', '')
        elif product_images:
            original_image = product_images[0].get('origin_url', '') or product_images[0].get('url', '')
            
        product_list_3.append(id)
        product_list_3.append(shop_name)
        product_list_3.append(name)
        product_list_3.append(original_price)
        product_list_3.append(discount_price)
        product_list_3.append(original_image)
        return product_list_3
    
    except Exception as e:
        print(f"상품 정보 추출 중 에러 ! : {e}")
        return []