import os
import sys
import pymongo
from bson.objectid import ObjectId
from datetime import datetime, timedelta, date
from persiantools.jdatetime import JalaliDate
import random 

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, root_path)

from models.app import *


def get_metadata(data):
    label = ','.join(list(data.keys()))
    value_data = ''.join([str(x)+',' for x in list(data.values())])[:-1]
    return label , value_data


def get_random_data(generation_rate:int, down_limit:int, up_limit:int):
    data = ''
    for i in range(generation_rate):
        if i < generation_rate-1:
            data += f"{random.randint(down_limit, up_limit)},"
        else:
            data += f"{random.randint(down_limit, up_limit)}"
    return data



class BaseOps:
    def __init__(self, post_model) -> None:
        self.post_model = post_model

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
                {"manual_info_service_tag": None},
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
        data = {'manual_info_service_tag': label}
        self.post_model.update(query, data)
        return True

    def get_statistics(self):
        today = datetime.combine(date.today(), datetime.min.time())
        date_ago = today - timedelta(days=90)
        space_days_range = 10
        data = {}
        data['entry'] = {}
        data['processed'] = {}
        data['junk'] = {}
        while date_ago <= today:
                data['entry'][JalaliDate(date_ago).strftime("%B %Y %d")] = self.post_model.collection.count_documents({"$and":[
                                                                        # {"sentiment":{"$in":["very_positive","positive"]}},
                                                                        {"created_at":{"$gt":date_ago}},
                                                                        {"created_at":{"$lte":date_ago + timedelta(days=space_days_range)}}
                                                                    ]})
                date_ago += timedelta(days=space_days_range)  
        # date_ago = today - timedelta(days=365)
        # while date_ago <= today:
        #         data['processed'][JalaliDate(date_ago).strftime("%B %Y %d")] = self.post_model.collection.count_documents({"$and":[
        #                                                                 {"ner":{"$ne":None}},
        #                                                                 {"created_at":{"$gt":date_ago}},
        #                                                                 {"created_at":{"$lte":date_ago + timedelta(days=30)}}
        #                                                             ]})
                
        #         date_ago += timedelta(days=30)  

        # date_ago = today - timedelta(days=365)
        # while date_ago <= today:
        #         data['junk'][JalaliDate(date_ago).strftime("%B %Y %d")] = self.post_model.collection.count_documents({"$and":[
        #                                                                 {"ner":[]},
        #                                                                 {"created_at":{"$gt":date_ago}},
        #                                                                 {"created_at":{"$lte":date_ago + timedelta(days=30)}}
        #                                                             ]})
                
        #         date_ago += timedelta(days=30)  
        data['processed'] = data['entry']
        data['junk'] = data['entry']
        label_chart11,data_chart11 = get_metadata(data['entry'])
        label_chart12,data_chart12 = get_metadata(data['processed'])
        label_chart13,data_chart13 = get_metadata(data['junk'])
        label_chart2,data_chart2 = get_metadata(data['entry'])
        label_chart3,data_chart3 = get_metadata(data['processed'])
        label_chart4 =  "نیروی زمینی,نیروی هوایی,نیروی دریایی,ستاد مشترک,حفاظت اطلاعات"
        data_chart4 = get_random_data(5,0,2000)
        return {
                "label_chart11":label_chart11,
                "data_chart11":data_chart11,
                "label_chart12":label_chart12,
                "data_chart12":data_chart12,
                "label_chart13":label_chart13,
                "data_chart13":data_chart13,
                "label_chart2":label_chart2,
                "data_chart2":data_chart2,
                "label_chart3":label_chart3,
                "data_chart3":data_chart3,
                "label_chart4":label_chart4,
                "data_chart4":data_chart4,
                }

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
        today = datetime.combine(date.today(), datetime.min.time())

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

        data_doc = self.post_model.collection.find(
            {"$and": [
                {"created_at": {"$gt": today - timedelta(days=day_limit)}},
                {"created_at": {"$lte": today}},
                {"category": category},
                {"manual_info_service_tag": inteligence_service_category},
                {"sentiment": sentiment},
                {"clean_context": {"$nin": [None, [], ""]}},
            ]}).skip(down_range).limit(up_range).sort('created_at', pymongo.DESCENDING)
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
            filter_date = datetime.fromisoformat(charts_time_filter)
            day_limit = today - filter_date
            day_limit = day_limit.days

        else:
            day_limit = 180
        info_tags = ['mali_tajhizat', 'nezami_aghidati', 'tahrik_eteraz',
                     'etemad_zodaei_modiriati', 'tazad_ekhtelaf', 'khodi', 'unknown']
        data = []
        for item in info_tags:
            data.append(self.post_model.collection.count_documents(
                {"$and": [
                    {"created_at": {"$gt": today - timedelta(days=day_limit)}},
                    {"created_at": {"$lte": today}},
                    {"manual_info_service_tag": item},
                ]}))
        data = str(data)
        return data

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

