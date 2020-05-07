import requests
import xml.etree.ElementTree as ET
import sys

_genreids = {
    "Action": 28, "Adventure": 12, "Animation": 16, "Comedy": 35, "Crime": 80, "Documentary": 99, "Drama": 18,
    "Family": 10751, "Fantasy": 14, "History": 36, "Horror": 27, "Kids": 10762, "Music": 10402, "Mystery": 9648,
    "News": 10763, "Reality": 10764, "Romance": 10749, "Science Fiction": 878, "Sci-Fi & Fantasy": 10765, "Soap": 10766,
    "Talk": 10767, "TV Movie": 10770, "Thriller": 53, "War": 10752, "War & Politics": 10768, "Western": 37}


class TMDb:
    def __init__(self, api_key=None, language=None, cache_long=None, cache_short=None, append_to_response=None, mpaa_prefix=None, filter_key=None, filter_value=None, exclude_key=None, exclude_value=None):
#	cache_short=cache_short
#	cache_long=cache_long
	req_api_name='TMDb'
	self.req_api_url='https://api.themoviedb.org/3'
#	req_wait_time=0.25

        req_api_key='?api_key=a07324c669cac4d96789197134ce272b'
        api_key = api_key if api_key else 'a07324c669cac4d96789197134ce272b'

        language = language if language else 'en-US'
        self.iso_language = language[:2]
        self.iso_country = language[-2:]
        self.req_language = '{0}-{1}&include_image_language={0},null'.format(self.iso_language, self.iso_country)
        self.req_api_key = '?api_key={0}'.format(api_key)
        self.req_append = append_to_response if append_to_response else None
        self.imagepath_original = 'https://image.tmdb.org/t/p/original'
        self.imagepath_poster = 'https://image.tmdb.org/t/p/w500'
        self.mpaa_prefix = '{0} '.format(mpaa_prefix) if mpaa_prefix else ''
        self.filter_key = filter_key if filter_key else None
        self.filter_value = filter_value if filter_value else None
        self.exclude_key = exclude_key if exclude_key else None
        self.exclude_value = exclude_value if exclude_value else None
        self.library = 'video'

#	self.tmdb = None
#	self.tvdb = None
#	self.imdb = None
	self.tvrage = None
#	self.original_name = None

    def dictify(r, root=True):
	    if root:
	        return {r.tag: dictify(r, False)}
	    d = copy(r.attrib)
	    if r.text:
	        d["_text"] = r.text
	    for x in r.findall("./*"):
	        if x.tag not in d:
	            d[x.tag] = []
	        d[x.tag].append(dictify(x, False))
	    return d

    def translate_xml(self, request):
        if request:
            request = ET.fromstring(request.content)
            request = self.dictify(request)
        return request

    def get_externalid_item(self, itemtype, external_id, external_source):
        """
        Lookup an item using an external id such as IMDb or TVDb
        """
        if not itemtype or not external_id or not external_source:
            return {}
        cache_name = '{0}.find.{1}.{2}'.format(self.cache_name, external_source, external_id)
        itemdict = self.get_cache(cache_name)
        if not itemdict:
            request = self.get_request('find', external_id, language=self.req_language, append_to_response=self.req_append, external_source=external_source)
            request = request.get('{0}_results'.format(itemtype), [])
            itemdict = self.set_cache(self.get_niceitem(request[0]), cache_name, self.cache_long) if request else {}
        if itemdict.get('tmdb_id'):
            itemdict = self.get_detailed_item(itemtype, itemdict.get('tmdb_id'), cache_only=True) or itemdict
        return itemdict

    def get_item_externalid(self, itemtype, tmdb_id, external_id=None):
        """
        Lookup external ids for an item using tmdb_id
        """
        if not itemtype or not tmdb_id:
            return {}
        request = self.get_request(itemtype, tmdb_id, 'external_ids') or {}
	print request
	self.tmdb = request.get('id')
	self.tvdb = request.get('tvdb_id')
	self.imdb = request.get('imdb_id')
	self.tvrage = request.get('tvrage_id')
        return request.get(external_id) if external_id else request

    def get_tmdb_id(self, itemtype=None, imdb_id=None, tvdb_id=None, query=None, year=None, selectdialog=False, usedetails=True, longcache=False, returntuple=False):
        func = self.get_request
        if not itemtype:
            return
        request = None
        if itemtype == 'genre' and query:
            return _genreids.get(query, '')
        elif imdb_id:
            request = func('find', imdb_id, language=self.req_language, external_source='imdb_id')
            request = request.get('{0}_results'.format(itemtype), [])
        elif tvdb_id:
            request = func('find', tvdb_id, language=self.req_language, external_source='tvdb_id')
            request = request.get('{0}_results'.format(itemtype), [])
        elif query:
            query = query.split(' (', 1)[0]  # Scrub added (Year) or other cruft in parentheses () added by Addons or TVDb
            if itemtype == 'tv':
                request = func('search', itemtype, language=self.req_language, query=query, first_air_date_year=year)
            else:
                request = func('search', itemtype, language=self.req_language, query=query, year=year)
            request = request.get('results', [])
        if not request:
            return
        itemindex = 0
#        if selectdialog:
#            item = utils.dialog_select_item(items=request, details=self, usedetails=usedetails)
#            if returntuple:
#                return (self.get_title(item), item.get('id')) if item else None
#            return item.get('id') if item else None
	self.original_name = request[itemindex].get('original_name')
        return request[itemindex].get('id')

    def get_request(self, *args, **kwargs):
        """ Get API request from cache (or online if no cached version) """
        cache_days = 0
        cache_name = ''
        cache_only = False
        cache_refresh = True
        is_json = kwargs.pop('is_json', True)
        request_url = self.get_request_url(*args, **kwargs)
        return self.get_api_request(request_url, is_json=is_json)

    def get_request_url(self, *args, **kwargs):
        """
        Creates a url request string:
        https://api.themoviedb.org/3/arg1/arg2?api_key=foo&kwparamkey=kwparamvalue
        """
        request = self.req_api_url
        for arg in args:
            if arg:  # Don't add empty args
                request = u'{0}/{1}'.format(request, arg)
        request = u'{0}{1}'.format(request, self.req_api_key)
        for key, value in kwargs.items():
            if value:  # Don't add empty kwargs
                sep = '?' if '?' not in request else ''
                request = u'{0}{1}&{2}={3}'.format(request, sep, key, value)
        return request

    def get_api_request(self, request=None, is_json=True, postdata=None, headers=None, dictify=True):
        """
        Make the request to the API by passing a url request string
        """
        try:
            response = requests.post(request, data=postdata, headers=headers) if postdata else requests.get(request, headers=headers)  # Request our data
        except Exception as err:
            return {} if dictify else None
        if not response.status_code == requests.codes.ok:  # Error Checking
            return {} if dictify else None
        if dictify and is_json:
            response = response.json()  # Make the response nice
        elif dictify:
            response = self.translate_xml(response)
        return response

    def originalname(self):

	return self.original_name

    def tmdb_id(self):
	return self.tmdb

    def tvdb_id(self):
	return self.tvdb

    def imdb_id(self):
	return self.imdb

    def tvrage_id(self):
	return self.tvrage

    def externalid_get(self, itemtype=None, tmdb_id=None, external_id=None):
	tmdb = TMDb()
	api_response = TMDb.get_item_externalid(tmdb, itemtype=itemtype, tmdb_id=tmdb_id, external_id=external_id)
#	print str(external_id) +' = '+ str(api_response)
	self.tvrage =  tmdb.tvrage
	self.tmdb = tmdb.tmdb
	self.tvdb = tmdb.tvdb
	self.imdb = tmdb.imdb

	return api_response

    def tmdb_id_get(self, itemtype=None, tvdb_id=None, query=None, year=None):
	tmdb = TMDb()
	api_response = TMDb.get_tmdb_id(tmdb, itemtype=itemtype, tvdb_id=tvdb_id, query=query)
#	print str('tmdb_id') +' = '+ str(api_response)
	self.original_name = tmdb.original_name
	return api_response

