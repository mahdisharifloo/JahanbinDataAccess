from utils.mongo import Mongo


class userModel(Mongo):
    _connection_name = 'mongo_connection1'
    _collection_name = 'users'
    _db_name = 'data_pipline'

class InstagramModel(Mongo):
    _connection_name = 'mongo_connection1'
    _collection_name = 'instagram_posts'
    _db_name = 'data_pipline'

class TwitterModel(Mongo):
    _connection_name = 'mongo_connection1'
    _collection_name = 'twitter_posts'
    _db_name = 'data_pipline'

class TelegramGroupModel(Mongo):
    _connection_name = 'mongo_connection1'
    _collection_name = 'telegram_group_posts'
    _db_name = 'data_pipline'

class TelegramChannelModel(Mongo):
    _connection_name = 'mongo_connection1'
    _collection_name = 'telegram_channel_posts'
    _db_name = 'data_pipline'

class NewsAgencyModel(Mongo):
    _connection_name = 'mongo_connection1'
    _collection_name = 'news_agency_posts'
    _db_name = 'data_pipline'


