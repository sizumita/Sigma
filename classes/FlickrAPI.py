import os
import flickrapi
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '../../sigma.env')
load_dotenv(dotenv_path)
app_id = os.environ.get("APP_ID")
api_key = os.environ.get("flickr_api_key")
secret = os.environ.get("flickr_select")


def flickr_get(keyword, num):
    flickr = flickrapi.FlickrAPI(api_key, secret, format='parsed-json')
    res = flickr.photos.search(
        text=keyword,
        per_page=num,
        media='photos',
        sort='relevance',
        safe_search=1,
        extras='url_q, licences'
    )
    return res
