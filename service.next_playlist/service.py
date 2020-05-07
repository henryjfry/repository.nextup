import time
import xbmc
import xbmcaddon
import xbmcgui
import json
import re
import urllib

import sys
import ntpath
import os.path

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')

global next_url
next_url = ''
db_path = str(xbmc.translatePath('special://database')) + 'MyVideos116.db'
update_playlist_path = str(xbmc.translatePath('special://userdata').replace('userdata','addons'))+str(__addonid__)

if ':' in update_playlist_path:
    update_playlist_path = update_playlist_path +'\emptywidget.xsp'
else:
    update_playlist_path = update_playlist_path +'/emptywidget.xsp'

#check whether or not playlist file exists create it if not (dummy playlist used to trigger widget updates)
if os.path.exists(update_playlist_path) == False:
    xml_playlist = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>' + "\n" + '<smartplaylist type="episodes">'
    xml_playlist = xml_playlist + "\n" + '<name>workaround for empty widget used for refreshes</name>' + "\n" + '<match>all</match>'
    xml_playlist = xml_playlist + "\n" + '<rule field="year" operator="greaterthan">' + "\n" + '<value>2200</value>' + "\n" + '</rule>'
    xml_playlist = xml_playlist + "\n" + '<limit>1</limit>' + "\n" +  '</smartplaylist>'
    f = open(update_playlist_path, "w")
    f.write(xml_playlist)
    f.close()

def movietitle_to_id(title):
        query = {
            "jsonrpc": "2.0",
            "method": "VideoLibrary.GetMovies",
            "params": {
                "properties": ["title"]
            },
            "id": "libMovies"
        }
        try:
            jsonrpccommand=json.dumps(query, encoding='utf-8')	
            rpc_result = xbmc.executeJSONRPC(jsonrpccommand)
            json_result = json.loads(rpc_result)
            if 'result' in json_result and 'movies' in json_result['result']:
                json_result = json_result['result']['movies']
                for movie in json_result:
                    # Switch to ascii/lowercase and remove special chars and spaces
                    # to make sure best possible compare is possible
                    titledb = movie['title'].encode('ascii', 'ignore')
                    titledb = re.sub(r'[?|$|!|:|#|\.|\,|\'| ]', r'', titledb).lower().replace('-', '')
                    if '(' in titledb:
                        titledb = titledb.split('(')[0]
                    titlegiven = title.encode('ascii','ignore')
                    titlegiven = re.sub(r'[?|$|!|:|#|\.|\,|\'| ]', r'', titlegiven).lower().replace('-', '')
                    if '(' in titlegiven:
                        titlegiven = titlegiven.split('(')[0]
                    if titledb == titlegiven:
                        return movie['movieid']
            return '-1'
        except Exception:
            return '-1' 

class XBMCPlayer( xbmc.Player ):

    def __init__( self, *args ):
        pass

    def onPlayBackStarted( self ):
	json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Title", "Player.Filenameandpath", "VideoPlayer.MovieTitle", "VideoPlayer.TVShowTitle", "VideoPlayer.DBID", "VideoPlayer.Duration", "VideoPlayer.Season", "VideoPlayer.Episode", "VideoPlayer.DBID", "VideoPlayer.Year", "VideoPlayer.Rating", "VideoPlayer.mpaa", "VideoPlayer.Studio", "VideoPlayer.VideoAspect", "VideoPlayer.Plot", "VideoPlayer.RatingAndVotes", "VideoPlayer.Genre", "VideoPlayer.LastPlayed", "VideoPlayer.IMDBNumber", "ListItem.DBID", "Container.FolderPath", "Container.FolderName", "Container.PluginName", "ListItem.TVShowTitle", "ListItem.FileNameAndPath"]}, "id":1}')
	json_object  = json.loads(json_result)
	title = ''
	Player_Filenameandpath = json_object['result']['Player.Filenameandpath']
	
	"""
	imdb_id = json_object['result']['VideoPlayer.IMDBNumber']
	if imdb_id == '':
		try: 
			imdb_id = re.search('imdb=(.+?)&', json_object['result']['Player.Filenameandpath']).group(1)
		except:
			imdb_id = '' 
	if imdb_id == '':
		try:
			imdb_url = str(json_object['result']['Player.Filenameandpath'])
			m = re.findall('=tt'+r'\d{6,7}', imdb_url)
			imdb = m[0].replace('=','')
			if 'tt' in imdb and len(imdb) == 9:
				imdb = imdb
			else:
				imdb_id = ''	
		except:
			imdb_id = '' 

#        xbmc.log(str(json_object)+'===>service.next_playlist1', level=xbmc.LOGNOTICE)
	"""

	if json_object['result']['VideoPlayer.TVShowTitle'] <> '':
		title = json_object['result']['VideoPlayer.TVShowTitle'] + ' - S'+str(json_object['result']['VideoPlayer.Season']).zfill(2) +'E'+str(json_object['result']['VideoPlayer.Episode']).zfill(2) +' - ' +  json_object['result']['VideoPlayer.Title']
		from resources.tmdb import TMDb
		objName = TMDb()
		query=json_object['result']['VideoPlayer.TVShowTitle']
		tmdb_query = objName.tmdb_id_get('tv',  query=query)
		objName.externalid_get('tv', tmdb_query, 'tvdb_id')
		tmdb_id = objName.tmdb_id()
		tvdb_id = objName.tvdb_id()


	"""
	url = "plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;query=" + urllib.quote_plus(json_object['result']['VideoPlayer.TVShowTitle']) + "&amp;season=" + str(json_object['result']['VideoPlayer.Season']) + "&amp;episode=" + str(json_object['result']['VideoPlayer.Episode']) 

        if json_object['result']['VideoPlayer.MovieTitle'] <> '':
		title = json_object['result']['VideoPlayer.MovieTitle']
		if imdb_id == '':
			url = u' '.join((json_object['result']['Player.Filenameandpath'])).encode('utf-8').replace("action=getSources&", "action=smartPlay&getSources=True&")
		else:
			url = "plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;imdb_id=" + imdb_id

	if json_object['result']['VideoPlayer.Title'] <> '' and title == '':
		title = json_object['result']['VideoPlayer.Title'] + ' (' + json_object['result']['VideoPlayer.Year'] + ')'

		if imdb_id == '':
			try: 
				imdb_id = re.search('imdb=(.+?)&', json_object['result']['Player.Filenameandpath']).group(1)
			except:
				imdb_id = '' 
		if imdb_id == '':
			try:
				imdb_url = str(json_object['result']['Player.Filenameandpath'])
				m = re.findall('=tt'+r'\d{6,7}', imdb_url)
				imdb = m[0].replace('=','')
				if 'tt' in imdb and len(imdb) == 9:
					imdb = imdb
				else:
					imdb_id = ''	
			except:
				imdb_id = '' 

		if imdb_id == '':
			url = str(json_object['result']['Player.Filenameandpath']).replace("action=getSources&", "action=smartPlay&getSources=True&")
		else:
			url = "plugin://plugin.video.themoviedb.helper?info=play&amp;type=movie&amp;imdb_id=" + imdb_id + "&amp;year=" + json_object['result']['VideoPlayer.Year']
	
	"""
        watched = 0
	global next_url
	next_url = ''
        while player.isPlaying()==1:
            xbmc.sleep(10000)
            if player.isPlayingVideo()==1 and watched == 0:
                json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Title", "Player.Filenameandpath", "VideoPlayer.MovieTitle", "VideoPlayer.TVShowTitle", "VideoPlayer.DBID", "VideoPlayer.Duration", "VideoPlayer.Season", "VideoPlayer.Episode", "VideoPlayer.DBID"]}, "id":1}')
                json_object  = json.loads(json_result)
                timestamp = json_object['result']['VideoPlayer.Duration']
                duration = reduce(lambda x, y: x*60+y, [int(i) for i in (timestamp.replace(':',',')).split(',')])
                dbID = json_object['result']['VideoPlayer.DBID']
                title = json_object['result']['VideoPlayer.Title']
                movie_title = json_object['result']['VideoPlayer.MovieTitle']
                tv_show_name = json_object['result']['VideoPlayer.TVShowTitle']
                season_num = json_object['result']['VideoPlayer.Season']
                ep_num = json_object['result']['VideoPlayer.Episode']
                movie_id = movietitle_to_id(title)
                try:
                    prev_ep_num = int(json_object['result']['VideoPlayer.Episode'])-1
                except:
                    prev_ep_num = ""
                    wacthed = 1
#                xbmc.log("PLAYBACK STARTED %s" % time.time() + '  ,'+str(dbID)+'=dbID, '+str(duration)+'=duration, '+str(tv_show_name)+'=tv_show_name, '+str(season_num)+'=season_num, '+str(ep_num)+'=ep_num, '+str(title)+', '+str(movie_title)+ '  ,'+str(movie_id)+'=movie_ID'+', '+str(prev_ep_num)+'=prev_ep_num', level=xbmc.LOGNOTICE)

                if str(movie_id) != str(-1):
                    wacthed = 1   
                    json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.GetMovieDetails","params":{"movieid":'+str(movie_id)+', "properties": ["playcount"]}}')
                    json_object  = json.loads(json_result)
	            play_count = int(json_object['result']['moviedetails']['playcount'])+1

	            while player.isPlayingVideo()==1 and watched == 0:
        	        xbmc.sleep(10000)
                        try:
                            percentage = (player.getTime() / duration) * 100
                        except:
                            watched = 1
                            break
                        if (percentage > 85) and player.isPlayingVideo()==1:
#                            xbmc.log(str(percentage)+'pc, '+str(movie_id)+'=dbID', level=xbmc.LOGNOTICE)
                            json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetMovieDetails","params":{"movieid":'+str(movie_id)+',"playcount": '+str(play_count)+'},"id":"1"}')
                            json_object  = json.loads(json_result)
        	            xbmc.log(str(json_object)+'=episode marked watched, '+str(movie_id)+'=dbID', level=xbmc.LOGNOTICE)
                            watched = 1
#                           break

                if dbID == "" and watched == 0:               
                    json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "params": {"sort": {"order": "ascending", "method": "title"}, "filter": {"operator": "is", "field": "title", "value": "'+tv_show_name+'"}, "properties": []}, "method": "VideoLibrary.GetTVShows", "id": 1}')
                    json_object  = json.loads(json_result)
                    try:
                        tv_show_num = json_object['result']['tvshows'][0]['tvshowid']
                    except:
                        watched = 1
                        return
                    json_result = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "id": 1 , "method": "VideoLibrary.GetEpisodes", "params": {"tvshowid": '+str(tv_show_num)+', "season": '+str(season_num)+', "properties": [], "limits": {"start": '+str(prev_ep_num)+', "end": '+str(ep_num)+'}}}')
                    json_object  = json.loads(json_result)

                    try:
                        dbID = json_object['result']['episodes'][0]['episodeid']
                    except:
                        watched = 1
                        return

                if dbID != "":   
                    json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","id":1,"method":"VideoLibrary.GetEpisodeDetails","params":{"episodeid":'+str(dbID)+', "properties": ["playcount"]}}')
                    json_object  = json.loads(json_result)
	            play_count = int(json_object['result']['episodedetails']['playcount'])+1

                    while player.isPlayingVideo()==1 and watched == 0:
                        xbmc.sleep(10000)
                        try:
                            percentage = (player.getTime() / duration) * 100
                        except:
                            watched = 1
                            break
                        if (percentage > 85) and player.isPlayingVideo()==1:
#                            xbmc.log(str(percentage)+'pc, '+str(dbID)+'=dbID', level=xbmc.LOGNOTICE)
                            json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"VideoLibrary.SetEpisodeDetails","params":{"episodeid":'+str(dbID)+',"playcount": '+str(play_count)+'},"id":"1"}')
                            json_object  = json.loads(json_result)
                            xbmc.log(str(json_object)+'=episode marked watched, '+str(dbID)+'=dbID', level=xbmc.LOGNOTICE)
                            watched = 1
####################################
			    
			    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		            current_position = playlist.getposition()
#			    xbmc.log(str(playlist.size())+' duration ===SERVICE_NEXT_PLAYLIST', level=xbmc.LOGNOTICE)
			    action = xbmcgui.Window(10000).getProperty('TMDbHelper.Player.Action')
#			    xbmc.log(str(action)+' action ===SERVICE_NEXT_PLAYLIST', level=xbmc.LOGNOTICE)

			    if playlist.size() < 2:
				xbmcgui.Window(10000).setProperty('TMDbHelper.Player.ResolvedUrl', 'true')
				playlist.clear()
				import sqlite3
				con = sqlite3.connect(db_path)
				cur = con.cursor()
				sql_result = cur.execute("SELECT strtitle, c12, c13, * from episode_view where idshow in (SELECT idshow from episode_view where idepisode = " + str(dbID) + ") and idepisode > " + str(dbID) + "  order by c05 limit 1").fetchall()
				try:
					strm_title = sql_result[0][0] + " - S" + str(sql_result[0][1]).zfill(2) + "E" + str(sql_result[0][2]).zfill(2) + " - " + sql_result[0][5]
				except:
					break

				if tmdb_id <> '':
					next_url = "plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tmdb_id=" + str(tmdb_id) + "&amp;season=" + str(sql_result[0][1]) + "&amp;episode=" + str(sql_result[0][2])
				elif tvdb_id <> '':
					next_url = "plugin://plugin.video.themoviedb.helper?info=play&amp;type=episode&amp;tvdb_id=" + str(tvdb_id) + "&amp;season=" + str(sql_result[0][1]) + "&amp;episode=" + str(sql_result[0][2])
#					next_url = "plugin://plugin.video.openmeta/tv/play/" + str(tvdb_id) + "/" + str(sql_result[0][1]) + "/" + str(sql_result[0][2])
				else:
					next_url = "plugin://plugin.video.themoviedb.helper?info=play4&amp;type=episode&amp;query=" + sql_result[0][0] + "&amp;season=" + str(sql_result[0][1]) + "&amp;episode=" + str(sql_result[0][2])

				listitem = xbmcgui.ListItem(strm_title, thumbnailImage=sql_result[0][11].replace('<thumb>','').replace('</thumb>',''))
				listitem.setInfo('video', {'Title': strm_title, 'Genre': sql_result[0][38]})
				listitem.setInfo('videos', {'mediatype' : 'episode'})
				playlist.add(url=next_url, listitem=listitem, index=1)
				cur.close()

				xbmc.log(str(next_url)+' added to playlist===SERVICE_NEXT_PLAYLIST', level=xbmc.LOGNOTICE)
				while player.isPlayingVideo()==1:
					try:					
					    player_time = player.getTime()
					except:
					    break
					percentage = (player_time / duration) * 100
					if percentage > 90 and player_time > (duration - 30):
						break
#				xbmcPlayer = xbmc.Player()
#				xbmcPlayer.play(playlist) 

##############################
				from resources.player import PlayerDialogs
				title = sql_result[0][5]
				thumb = sql_result[0][11].replace('<thumb>','').replace('</thumb>','')
				show = sql_result[0][0]
				season = sql_result[0][1]
				episode = sql_result[0][2]
				try: 
					year = sql_result[0][35][:4]
				except:
					year = ''
				try:
					rating = sql_result[0][45]
				except:
					rating = ''
				PlayerDialogs().display_dialog(next_url, title, thumb, rating, show, season, episode, year)

    def onPlayBackEnded( self ):
	xbmcgui.Window(10000).clearProperty('TMDbHelper.Player.ResolvedUrl')
	if next_url <> '':
     		xbmc.executebuiltin('RunPlugin(%s)' % next_url)
        kodi_playlist_generate()

    def onPlayBackStopped( self ):
        kodi_playlist_generate()

class KodiMonitor(xbmc.Monitor):

    def __init__(self, **kwargs):
        xbmc.Monitor.__init__(self)

    def onDatabaseUpdated(self, database):
        if database == "video":
	    kodi_playlist_generate()

    def onNotification(self, sender, method, data):
        if (method == 'VideoLibrary.OnUpdate'):
            kodi_playlist_generate()

def kodi_playlist_generate():

	mysql_enabled = __addon__.getSetting('mysql_enabled')

	if mysql_enabled == 'false':
		import sqlite3
		#con = sqlite3.connect('/home/osmc/.kodi/userdata/Database/MyVideos116.db')
		con = sqlite3.connect(db_path)

	if mysql_enabled == 'true':
		import mysql.connector
		sql_username = __addon__.getSetting('username')
		sql_password = __addon__.getSetting('password')
		sql_host = __addon__.getSetting('host')
		sql_port = __addon__.getSetting('port')
		sql_db_name = __addon__.getSetting('db_name')
		con = mysql.connector.connect(host=sql_host, user=sql_username, passwd=sql_password, port=sql_port, db=sql_db_name)

	cur = con.cursor()
#	playlist_path = 'special://profile/playlists/video'
	playlist_path = str(xbmc.translatePath('special://profile/playlists/video')) + '/'

	sql_method = int(__addon__.getSetting('sql_method'))+1

	if sql_method == 1:
	#next up tv shows (in progress only) ordered by airdate
		cur.execute("select idepisode, c18, c13, tvshow1, genre, idshow, idseason, episode1 from (select idseason, files.idfile, episode.c00 as episode1, episode.c18, episode.c12, episode.c13, episode.c05, tvshow.c08 as genre, idepisode, tvshow.c00 as tvshow1, episode.idShow, playcount, lastplayed from episode, files, tvshow where (episode.idfile = files.idfile) and (episode.idshow = tvshow.idshow) and files.idfile in (select idfile from (select min(files.idfile) as idfile, min(episode.c05) as firstaired, tvshow.c00 from episode, files, tvshow where (episode.idfile = files.idfile) and (episode.idshow = tvshow.idshow) and playcount is null group by tvshow.c00) as a)) as b where (idshow in (select idshow from (select files.idfile, episode.c00 as episode1, episode.c05, idepisode, tvshow.c00 as tvshow1, episode.idShow, playcount, lastplayed from episode, files, tvshow where (episode.idfile = files.idfile) and (episode.idshow = tvshow.idshow) and files.idfile in (select idfile from (select max(files.idfile) as idfile, max(episode.c05) as firstaired, tvshow.c00 from episode, files, tvshow where (episode.idfile = files.idfile) and (episode.idshow = tvshow.idshow) and playcount > 0 group by tvshow.c00) as c))as d)) and c05 < current_date order by c05 desc;")
		sql_result = cur.fetchall()

	if sql_method == 2:
	#next up all tv shows ordered by airdate
		cur.execute("select idepisode, c18, c13, tvshow1, genre, idshow, idseason from (SELECT idseason, files.idfile, episode.c00 as episode1, episode.c18, episode.c12, episode.c13, episode.c05, tvshow.c08 as genre, idepisode, tvshow.c00 as tvshow1, episode.idShow, playcount, lastplayed from episode, files, tvshow where (episode.idfile = files.idfile) and (episode.idshow = tvshow.idshow) and files.idfile in (select idfile from (SELECT min(files.idfile) as idfile, min(episode.c05) as firstaired, tvshow.c00 FROM episode, files, tvshow where (episode.idfile = files.idfile) and (episode.idshow = tvshow.idshow) and playcount is null GROUP BY tvshow.c00) as a)) as b where c05 < current_date order by c05 desc;")
		sql_result = cur.fetchall()


	big_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>' + "\n" + '<smartplaylist type="episodes">'  + "\n" 
	big_xml = big_xml + '    <name>NEXT EPISODES PLAYLIST</name>' + "\n" + '    <match>one</match>'

	for k in sql_result:
		path_str = k[1]
		base_name = ntpath.basename(path_str)
		big_xml = big_xml + "\n" + '    <rule field=\"filename\" operator=\"is\"><value>'+ base_name +'</value></rule>'

        sort_order_str = str(__addon__.getSetting('sort_order_str'))
        sort_order_direction = str(__addon__.getSetting('sort_order_direction'))
	big_xml = big_xml + "\n"+'    <order direction=\"'+sort_order_direction+'ending\">'+sort_order_str+'</order><virtualfolder>true</virtualfolder></smartplaylist>'

	f = open(playlist_path + "NEXT_EPISODES_PLAYLIST.xsp", "w")
	f.write(big_xml)
	f.close()

	cur.close()
#        xbmc.log(sort_order_direction+sort_order_str+"PLAYLIST!!!!! %s" % time.time(), level=xbmc.LOGNOTICE)
	pass

player = XBMCPlayer()
monitor = KodiMonitor()

while(not xbmc.abortRequested):
    xbmc.sleep(500)