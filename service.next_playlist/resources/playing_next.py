import xbmc
import xbmcaddon
import json
import re
from resources.base_window import BaseWindow

class PlayingNext(BaseWindow):

    def __init__(self, xml_file, xml_location, actionArgs=None):

	try:
	    self.player = xbmc.Player()
	except:
	    self.close()
	    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
	    exit()
#            return	

        try:
            super(PlayingNext, self).__init__('playing_next.xml', xbmcaddon.Addon().getAddonInfo('path').decode('utf-8'), actionArgs=actionArgs)
#	    dialog = xbmcgui.WindowXMLDialog('playing_next.xml', xbmcaddon.Addon().getAddonInfo('path').decode('utf-8'))
#	    dialog.doModal()
	    
	    self.next_url = re.findall(r'([^\[\]]*)', actionArgs)[1]
	    self.title = re.findall(r'([^\[\]]*)', actionArgs)[4]
	    self.thumb = re.findall(r'([^\[\]]*)', actionArgs)[7]
	    self.rating = re.findall(r'([^\[\]]*)', actionArgs)[10]
	    self.show = re.findall(r'([^\[\]]*)', actionArgs)[13]
	    self.season = re.findall(r'([^\[\]]*)', actionArgs)[16]
	    self.episode = re.findall(r'([^\[\]]*)', actionArgs)[19]
	    self.year = re.findall(r'([^\[\]]*)', actionArgs)[22]

#            self.player = xbmc.Player()
	    try:
		    self.remaining_time = int(self.player.getTotalTime()) - int(self.player.getTime())
	    except:
		    self.close()
                    return	
	    self.percent_decrease = (0.5 / self.remaining_time) * 100
            self.playing_file = self.player.getPlayingFile()
	    try:
	        self.duration = int(self.player.getVideoInfoTag().getDuration())
	    except:
		self.close()
	        return		
            self.closed = False
            self.actioned = None

            json_result = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"XBMC.GetInfoLabels","params": {"labels":["VideoPlayer.Title", "Player.Filenameandpath", "VideoPlayer.MovieTitle", "VideoPlayer.TVShowTitle", "VideoPlayer.DBID", "VideoPlayer.Duration", "VideoPlayer.Season", "VideoPlayer.Episode", "VideoPlayer.DBID"]}, "id":1}')
            json_object  = json.loads(json_result)
            timestamp = json_object['result']['VideoPlayer.Duration']
            self.duration = reduce(lambda x, y: x*60+y, [int(i) for i in (timestamp.replace(':',',')).split(',')])

#	    xbmc.log(str(xml_file)+' ===SEREN_PLAYER', level=xbmc.LOGNOTICE)
#            xbmc.log(str(xml_location)+' ===SEREN_PLAYER', level=xbmc.LOGNOTICE)
#	    xbmc.log(str(actionArgs)+' ===SEREN_PLAYER', level=xbmc.LOGNOTICE)

        except:
            import traceback
            traceback.print_exc()

    def onInit(self):
        self.background_tasks()

    def calculate_percent(self):
        xbmc.log(str(((int(self.player.getTotalTime()) - int(self.player.getTime())) / int(self.remaining_time)) * 100)+' ===PLAYING_NEXT', level=xbmc.LOGNOTICE)

        return ((int(self.player.getTotalTime()) - int(self.player.getTime())) / int(self.remaining_time)) * 100

    def background_tasks(self):
        try:
            try:
                progress_bar = self.getControl(3014)
            except:
                progress_bar = None

	    try:
		self.player.getTime()
	    except:
		self.close()
		return

	    percent = 100
            while 120 > (int(self.player.getTotalTime()) - int(self.player.getTime())) > 1 and not self.closed:
#            while not self.closed:
                xbmc.sleep(500)
                if progress_bar is not None:
		    percent = float(percent) - self.percent_decrease
                    progress_bar.setPercent(percent)

#            if self.playing_file == self.player.getPlayingFile() and not self.actioned:
#                self.player.pause()
        except:
            import traceback
            traceback.print_exc()
            pass

        self.close()

    def doModal(self):

        try:
            super(PlayingNext, self).doModal()
        except:
            import traceback
            traceback.print_exc()

    def close(self):
        self.closed = True
        super(PlayingNext, self).close()

    def onClick(self, control_id):
        self.handle_action(7, control_id)

    def handle_action(self, action, control_id=None):
        if control_id is None:
            control_id = self.getFocusId()

        if control_id == 3001:
            self.actioned = True
	    """
	    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	    current_position = playlist.getposition()
       	    xbmc.log(str(playlist.size())+' duration ===PLAYING_NEXT', level=xbmc.LOGNOTICE)
            try:
		xbmc.log(str(playlist[0].getPath())+'0 ===PLAYING_NEXT', level=xbmc.LOGNOTICE)
		xbmc.log(str(playlist[1].getPath())+'1 ===PLAYING_NEXT', level=xbmc.LOGNOTICE)
	    except:
		pass
            xbmcPlayer = xbmc.Player()
            self.close()
	    xbmcPlayer.play(playlist) 
#	    self.player.seekTime(self.player.getTotalTime())
#	    xbmc.executebuiltin('PlayerControl(BigSkipForward)')
	    """
	    import xbmcgui
    	    xbmcgui.Window(10000).clearProperty('TMDbHelper.Player.ResolvedUrl')
            self.close()
	    self.player.stop()
	    xbmc.executebuiltin('RunPlugin(%s)' % self.next_url)
        if control_id == 3002:
            self.actioned = True
            self.close()

    def onAction(self, action):

        action = action.getId()

        if action == 92 or action == 10:
            # BACKSPACE / ESCAPE
            self.close()

        if action == 7:
            self.handle_action(action)
            return

