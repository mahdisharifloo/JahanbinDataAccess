import os
import sys
import pymongo
import re 
from bson.objectid import ObjectId
from datetime import datetime, timedelta, date
from persiantools.jdatetime import JalaliDate


import random
import requests
import json
from wordcloud_fa import WordCloudFa

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_path)
from models.app import *

wc = WordCloudFa(
    # font_path="components/Vazir-Thin.ttf",
    # mask=mask_array,
    persian_normalize=True,
    no_reshape=True,
    collocations=False,
    stopwords=set([]),
    # background_color='white',
)


brian_mission = {
    "mali_tajhizat": "بزرگنمایی مشکلات و نارسایی ها",
    "nezami_aghidati": "القائ ضعف اعتقادی در آجا",
    "tahrik_eteraz": "تحریک کارکنان و تشویش اذهان آنها",
    "etemad_zodaei_modiriati": "بزرگنمایی مشکلات مدیریتی و اعتمادزدایی",
    "tazad_ekhtelaf": "بزرگنمایی تضادها و اختلاف ها",
    "khodi": "اقدام خودی",
    "unknown": "نامشخص",
}


def get_metadata(data):
    label = ','.join(list(data.keys()))
    value_data = ''.join([str(x)+',' for x in list(data.values())])[:-1]
    return label, value_data


def get_random_data(generation_rate: int, down_limit: int, up_limit: int):
    data = ''
    for i in range(generation_rate):
        if i < generation_rate-1:
            data += f"{random.randint(down_limit, up_limit)},"
        else:
            data += f"{random.randint(down_limit, up_limit)}"
    return data


def get_category(caption):
    url = "http://94.182.215.116:10034/category"
    querystring = {"prompt": caption}
    payload = ""
    headers = {"accept": "application/json"}
    response = requests.request(
        "POST", url, data=payload, headers=headers, params=querystring)
    resp = response.text
    resp = resp.replace('"', '')
    return resp


def get_sentiment(caption):
    url = "http://94.182.215.116:10031/sentiment_analysis"
    querystring = {"prompt": caption}
    payload = ""
    headers = {"accept": "application/json"}
    response = requests.request(
        "POST", url, data=payload, headers=headers, params=querystring)
    resp = json.loads(response.text)
    return resp[0]


# class BaseRules:
#     def __init__(self):
#         self.knowledge_base = [
#             {"word": "سرباز","do": ""}
#         ]
#     def check_with_knowledge_base(self,caption):
#         return caption


class BaseOps:
    def __init__(self, post_model) -> None:
        self.post_model = post_model
        # self.rules = BaseRules()

    def get_records(self, sentiment='', category='',
                    inteligence_service_category='',
                    time_filtering="6m", count=10):
        if not sentiment:
            sentiment = {"$ne": None}
        if not category:
            category = {"$ne": None}
        if not inteligence_service_category:
            inteligence_service_category = {"$ne": None}
        if time_filtering == "1d":
            day_limit = 1
        if time_filtering == "3d":
            day_limit = 3
        if time_filtering == "7d":
            day_limit = 7
        if time_filtering == "14d":
            day_limit = 14
        if time_filtering == "1m":
            day_limit = 30
        if time_filtering == "2m":
            day_limit = 60
        if time_filtering == "3m":
            day_limit = 90
        if time_filtering == "6m":
            day_limit = 180
        if time_filtering == "1y":
            day_limit = 360
        today = datetime.combine(date.today(), datetime.min.time())
        data_doc = self.post_model.collection.find(
            {"$and": [
                {"information_service_tag": inteligence_service_category},
                {"created_at": {"$gt": today - timedelta(days=day_limit)}},
                {"created_at": {"$lte": today}},
                {"category": category},

                {"sentiment": sentiment},
                {"clean_context": {"$nin": [None, [], ""]}},
            ]}).sort('created_at', pymongo.DESCENDING).limit(int(count))
        data = [doc for doc in data_doc]
        for d in data:
            d['_id'] = str(d['_id'])
        return data

    def last_news(self, count=5):
        data_doc = self.post_model.collection.find(
            {"$and": [
                {"clean_context": {"$nin": [None, [], ""]}},
            ]}).sort('created_at', pymongo.DESCENDING).limit(int(count))
        data = [doc for doc in data_doc]
        for d in data:
            d['_id'] = str(d['_id'])
        return data

    def add_info_service_tag(self, record_id, label):
        query = {"_id": ObjectId(record_id)}
        data = {'information_service_tag': label}
        self.post_model.update(query, data)
        return True

    def get_statistics(self):
        today = datetime.combine(date.today(), datetime.min.time())
        date_ago = today - timedelta(days=90)
        space_days_range = 10
        data = []
        while date_ago <= today:
            data.append({
                "name": JalaliDate(date_ago).strftime("%B %Y %d"),
                "value":  self.post_model.collection.count_documents({"$and": [
                    {"created_at": {"$gt": date_ago}},
                    {"created_at": {"$lte": date_ago +
                                    timedelta(days=space_days_range)}}
                ]})
            })
            date_ago += timedelta(days=space_days_range)
        return data

    def get_news(self, page=1,
                 sentiment='',
                 category='',
                 inteligence_service_category='',
                 time_filtering="6m",):
        if not page:
            page = 1
        if type(page) == str:
            page = int(page)
        if not sentiment:
            sentiment = {"$ne": None}
        if not category:
            category = {"$ne": None}
        if not inteligence_service_category:
            inteligence_service_category = {"$ne": None}
        today = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1)

        if time_filtering == "1d":
            day_limit = 1
        if time_filtering == "3d":
            day_limit = 3
        if time_filtering == "7d":
            day_limit = 7
        if time_filtering == "14d":
            day_limit = 14
        if time_filtering == "1m":
            day_limit = 30
        if time_filtering == "2m":
            day_limit = 60
        if time_filtering == "3m":
            day_limit = 90
        if time_filtering == "6m":
            day_limit = 180
        if time_filtering == "1y":
            day_limit = 360

        data_viwe_range = 10
        down_range = (page-1) * data_viwe_range
        up_range = (page-1) * data_viwe_range + data_viwe_range

        if page == 1:
            previews_page = 1
        else:
            previews_page = page - 1
        next_page = page + 1
        next_next_page = page + 2

        if previews_page != page:
            pages = [
                {"url": f'/news/?page={previews_page}', "number": previews_page},
                {"url": f'/news/?page={page}', "number": page},
                {"url": f'/news/?page={next_page}', "number": next_page},
                {"url": f'/news/?page={next_next_page}', "number": next_next_page}
            ]
        else:
            pages = [
                {"url": f'/news/?page={page}', "number": page},
                {"url": f'/news/?page={next_page}', "number": next_page},
                {"url": f'/news/?page={next_next_page}', "number": next_next_page}
            ]
        query = {"$and": [
                {"created_at": {"$gt": today - timedelta(days=day_limit)}},
                {"created_at": {"$lte": today}},
                {"category": category},
                {"information_service_tag": inteligence_service_category},
                {"sentiment": sentiment},
                {"clean_context": {"$nin": [None, [], ""]}},
            ]}
        data_doc = self.post_model.collection.find(query).sort('created_at', pymongo.DESCENDING).skip(down_range).limit(up_range)
        data = [doc for doc in data_doc]

        for d in data:
            d['_id'] = str(d['_id'])
        return data, pages

    def search_news(self, query, page=1, time_filtering="6m"):
        if not page:
            page = 1
        if type(page) == str:
            page = int(page)
        if time_filtering == "1d":
            day_limit = 1
        if time_filtering == "3d":
            day_limit = 3
        if time_filtering == "7d":
            day_limit = 7
        if time_filtering == "14d":
            day_limit = 14
        if time_filtering == "1m":
            day_limit = 30
        if time_filtering == "2m":
            day_limit = 60
        if time_filtering == "3m":
            day_limit = 90
        if time_filtering == "6m":
            day_limit = 180
        if time_filtering == "1y":
            day_limit = 360
        today = datetime.combine(date.today(), datetime.min.time())

        data_viwe_range = 10
        down_range = (page-1) * data_viwe_range
        up_range = (page-1) * data_viwe_range + data_viwe_range

        if page == 1:
            previews_page = 1
        else:
            previews_page = page - 1
        next_page = page + 1
        next_next_page = page + 2

        if previews_page != page:
            pages = [
                {"url": f'/news/?query={query}&page={previews_page}',
                    "number": previews_page},
                {"url": f'/news/?query={query}&page={page}', "number": page},
                {"url": f'/news/?query={query}&page={next_page}', "number": next_page},
                {"url": f'/news/?query={query}&page={next_next_page}',
                    "number": next_next_page}
            ]
        else:
            pages = [
                {"url": f'/news/?query={query}&page={page}', "number": page},
                {"url": f'/news/?query={query}&page={next_page}', "number": next_page},
                {"url": f'/news/?query={query}&page={next_next_page}',
                    "number": next_next_page}
            ]

        data_doc = self.post_model.collection.find(
            {"$and": [
                {"created_at": {"$gt": today - timedelta(days=day_limit)}},
                {"created_at": {"$lte": today}},
                {"clean_context": {
                    "$regex": f"/*{query}/*"}}
            ]}
        ).skip(down_range).limit(up_range).sort('created_at', pymongo.DESCENDING)
        data = [doc for doc in data_doc]

        for d in data:
            d['_id'] = str(d['_id'])

        return data, pages

    def get_sunburst_chart_data(self, charts_time_filter=None):
        today = datetime.combine(date.today(), datetime.min.time())
        if charts_time_filter:
            y,m,d = charts_time_filter.split("-")
            if len(m) == 1:
                m = '0'+m
            if len(d) == 1:
                d = '0'+d
            
            charts_time_filter = y+'-'+m+'-'+d + 'T00:00:00'
            filter_date = JalaliDate.fromisoformat(charts_time_filter)
            converted_filter_date = filter_date.to_gregorian()
            converted_filter_datetime = datetime.combine(converted_filter_date, datetime.min.time())

            day_limit = today - converted_filter_datetime
            day_limit = day_limit.days

        else:
            day_limit = 180
        info_tags = {
            1: "بزرگنمایی مشکلات و نارسایی ها",
            2: "القائ ضعف اعتقادی در آجا",
            3: "تحریک کارکنان و تشویش اذهان آنها",
            4: "بزرگنمایی مشکلات مدیریتی و اعتمادزدایی",
            5: "بزرگنمایی تضادها و اختلاف ها",
            6: "اقدام خودی"
        }
        data = []
        for item in info_tags.values():
            data.append(
                {
                    "name": item,
                    "value": self.post_model.collection.count_documents(
                        {"$and": [
                            {"created_at": {"$gt": today -
                                            timedelta(days=day_limit)}},
                            {"created_at": {"$lte": today}},
                            {"information_service_tag": item},
                        ]})}
            )
        # data = str(data)
        return data

    def get_rule_base_info_service_tag(self, caption):
        category = get_category(caption)
        sentiment = get_sentiment(caption)
        decisions = {
            1: "بزرگنمایی مشکلات و نارسایی ها",
            2: "القائ ضعف اعتقادی در آجا",
            3: "تحریک کارکنان و تشویش اذهان آنها",
            4: "بزرگنمایی مشکلات مدیریتی و اعتمادزدایی",
            5: "بزرگنمایی تضادها و اختلاف ها",
            6: "اقدام خودی",
            7: "نامشخص"
        }
        decisions_makes = []
        valid_categories = [
            "اقتصادی",
            "بین الملل",
            "اجتماعی",
            "سیاسی",
        ]
        khodi_list = [
            "نیرو","شهید","فرمانده",
            "نزاجا","نهاجا","نداجا",
            "زمینی","هوایی","دریایی",
            "دفاع","شناور","یگان",
        ]
        modiriati = [
            "مدیر","مسئول","معاول",
            "رئیس","کمیسیون","پارلمان"
        ]
        naresayei = [
            "پول","مال","هزینه",
            "مسکن","خونه","اجاره",
            "سند","سازمان",
        ]
        tahrik = [
            "آزادی","اعتراض","تحریک"
            "خامنه","اعتراض","تحریک"
        ]
        tazad = [
            "آخوند","عرزشی","ارزشی"
            "بسیجی","مزدور","خرزشی"
        ]
        eteghadi = [
            "حجاب","دین","اسلام"
            "حجاب","امام","امام"
        ]
        
        if category in valid_categories:
            for item in khodi_list:
                if item in caption:
                    return decisions[6]
                
            for item in modiriati:
                if item in caption:
                    return decisions[4]
            
                
            for item in naresayei:
                if item in caption:
                    return decisions[1]
            
                
            for item in tahrik:
                if item in caption:
                    return decisions[3]
            
                
            for item in tazad:
                if item in caption:
                    return decisions[5]
            
                
            for item in eteghadi:
                if item in caption:
                    return decisions[2]
            

            if category == valid_categories[0]:
                return random.choice(
                    [decisions[1], decisions[4] ])
            if sentiment in ['positive', "very positive", "mixed"] :
                return decisions[6]
            choice = random.choice([
                decisions[2], decisions[3],decisions[5]
            ])
            return choice
        else:
            return "نامشخص"

    def generate_word_frequencies(self, days_ago=30):
        delta_blow = datetime.now() - timedelta(days=days_ago)
        delta_head = datetime.now()
        query = {"$and": [
                {"ner": {"$nin": [None, []]}},
                {"created_at": {"$gt": delta_blow}},
                {"created_at": {"$lte": delta_head}}
        ]}
        posts_iterator = self.post_model.collection.find(query)
        data = [doc for doc in posts_iterator]
        words = []
        for d in data:
            ner = d['ner']
            for item in ner:
                words.append(item['word'].replace(' ', '-'))
        text = ' '.join(words)
        frequencies = wc.process_text(text)
        out = []
        for k, v in zip(frequencies.keys(), frequencies.values()):
            record = {}
            if v > 10 and len(k) > 2 and "#" not in k:
                record['text'] = k
                record["value"] = v
                out.append(record)
        return out


class InstagramOps(BaseOps):
    def __init__(self) -> None:
        post_model = InstagramModel()
        super().__init__(post_model)


class TwitterOps(BaseOps):
    def __init__(self) -> None:
        post_model = TwitterModel()
        super().__init__(post_model)


class TelegramGroupOps(BaseOps):
    def __init__(self) -> None:
        post_model = TelegramGroupModel()
        super().__init__(post_model)


class TelegramChannelOps(BaseOps):
    def __init__(self) -> None:
        post_model = TelegramChannelModel()
        super().__init__(post_model)


class NewsAgencyOps(BaseOps):
    def __init__(self) -> None:
        post_model = NewsAgencyModel()
        super().__init__(post_model)
