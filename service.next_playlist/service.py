import time
import xbmc
import xbmcaddon
#import json

import sys
import ntpath
#import sqlite3
import os.path

__addon__        = xbmcaddon.Addon()
__addonid__      = __addon__.getAddonInfo('id')

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

class XBMCPlayer( xbmc.Player ):

    def __init__( self, *args ):
        pass

    def onPlayBackStarted( self ):
#        Will be called when xbmc starts playing a file
#        xbmc.log(str(player.isPlaying()), level=xbmc.LOGNOTICE)
        while player.isPlayingVideo()==0:
            xbmc.sleep(500)
#            if player.isPlayingVideo():
#                xbmc.log('PLAYINGVIDEO=TRUE'+str("%s") % time.time(), level=xbmc.LOGNOTICE)
#                xbmc.log("PLAYBACK STARTED %s" % time.time(), level=xbmc.LOGNOTICE)

    def onPlayBackEnded( self ):
#        Will be called when xbmc stops playing a file
#        xbmc.log(str(player.isPlayingVideo()==True)+"%s" % time.time(), level=xbmc.LOGNOTICE)
#        xbmc.log("PLAYBACK ENDED %s" % time.time(), level=xbmc.LOGNOTICE)
        kodi_playlist_generate()

    def onPlayBackStopped( self ):
#        Will be called when user stops xbmc playing a file
#        xbmc.log("PLAYBACK STOPPED %s" % time.time(), level=xbmc.LOGNOTICE)
        kodi_playlist_generate()

class KodiMonitor(xbmc.Monitor):

    def __init__(self, **kwargs):
        xbmc.Monitor.__init__(self)

    def onDatabaseUpdated(self, database):
        if database == "video":
	    kodi_playlist_generate()
#            xbmc.log("LIBRARY SCAN! %s" % time.time(), level=xbmc.LOGNOTICE)

    def onNotification(self, sender, method, data):
        if (method == 'VideoLibrary.OnUpdate'):
            kodi_playlist_generate()
#            xbmc.log("WATCHED/UNWATCHED %s" % time.time(), level=xbmc.LOGNOTICE)
#            response = json.loads(data)          
#            if (response.has_key('item') and response['item'].has_key('type') and response.get('item').get('type') == 'episode'): # Episode means it is a TV show
#                episodeid = response.get('item').get('id')
#                playcount = response.get('playcount')
#                if (playcount > 0): # If it has been watched 
#                    xbmc.log("WATCHED! %s" % time.time(), level=xbmc.LOGNOTICE)


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