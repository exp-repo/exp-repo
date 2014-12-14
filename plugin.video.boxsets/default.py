# -*- coding: utf-8 -*-
# This plugin is an edited version of Divingmule's LiveStreams plugin. "Big thanks to Divingmule"
# The purpose of this plugin is to provide a live streaming of Filipino TV Channels.
# All the channels are being hosted from different websites, put together in one dedicated xml file.

import urllib
import urllib2
import datetime
import re
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup, BeautifulSOAP
try:
    import json
except:
    import simplejson as json

addon = xbmcaddon.Addon(id='plugin.video.boxsets')
profile = addon.getAddonInfo('profile').decode('utf-8')
home = addon.getAddonInfo('path').decode('utf-8')
favorites = xbmc.translatePath(os.path.join(profile, 'favorites' )).decode('utf-8')
icon = xbmc.translatePath(os.path.join(home, 'icon.png'))
fanart = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))
if os.path.exists(favorites)==True:
    FAV = open(favorites).read()

data = 'http://raw.github.com/exp-repo/exp-repo/master/box_sets.xml'


def makeRequest(url, headers=None):
        try:
            if headers is None:
                headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'}
            req = urllib2.Request(url,None,headers)
            response = urllib2.urlopen(req)
            data = response.read()
            response.close()
            return data
        except urllib2.URLError, e:
            print 'URL: '+url
            if hasattr(e, 'code'):
                print 'We failed with error code - %s.' % e.code
                xbmc.executebuiltin("XBMC.Notification(BoxSets, We failed with error code - "+str(e.code)+",10000,"+icon+")")
            elif hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: %s' %e.reason
                xbmc.executebuiltin("XBMC.Notification(BoxSets, We failed to reach a server. - "+str(e.reason)+",10000,"+icon+")")


def getSoup(url):
        if url.startswith('http://'):
            data = makeRequest(url)
        else:
            if xbmcvfs.exists(url):
                if url.startswith("smb://"):
                    copy = xbmcvfs.copy( url, xbmc.translatePath(os.path.join(profile, 'temp', 'sorce_temp.txt')))
                    if copy:
                        data = open( xbmc.translatePath(os.path.join(profile, 'temp', 'sorce_temp.txt')), "r").read()
                        xbmcvfs.delete( xbmc.translatePath(os.path.join(profile, 'temp', 'sorce_temp.txt')) )
                    else:
                        print "--- failed to copy from smb: ---"
                else:
                    data = open(url, 'r').read()
            else:
                print "--- Soup Data not found! ---"
                return
        soup = BeautifulSOAP(data, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
        return soup


def getData(url,fanart):
        soup = getSoup(url)
        if len(soup('channels')) > 0:
            channels = soup('channel')
            for channel in channels:
                name = channel('name')[0].string
                thumbnail = channel('thumbnail')[0].string
                if thumbnail == None:
                    thumbnail = ''

                try:
                    if not channel('fanart'):
                        if addon.getSetting('use_thumb') == "true":
                            fanArt = thumbnail
                        else:
                            fanArt = fanart
                    else:
                        fanArt = channel('fanart')[0].string
                    if fanArt == None:
                        raise
                except:
                    fanArt = fanart

                try:
                    desc = channel('info')[0].string
                    if desc == None:
                        raise
                except:
                    desc = ''

                try:
                    genre = channel('genre')[0].string
                    if genre == None:
                        raise
                except:
                    genre = ''

                try:
                    date = channel('date')[0].string
                    if date == None:
                        raise
                except:
                    date = ''
                try:
                    addDir(name.encode('utf-8', 'ignore'),url.encode('utf-8'),2,thumbnail,fanArt,desc,genre,date)
                except:
                    print 'There was a problem adding directory from getData(): '+name.encode('utf-8', 'ignore')
        else:
            getItems(soup('item'),fanart)


def getChannelItems(name,url,fanart):
        soup = getSoup(url)
        channel_list = soup.find('channel', attrs={'name' : name})
        items = channel_list('item')
        try:
            fanArt = channel_list('fanart')[0].string
            if fanArt == None:
                raise
        except:
            fanArt = fanart
        for channel in channel_list('subchannel'):
            name = channel('name')[0].string
            try:
                thumbnail = channel('thumbnail')[0].string
                if thumbnail == None:
                    raise
            except:
                thumbnail = ''
            try:
                if not channel('fanart'):
                    if addon.getSetting('use_thumb') == "true":
                        fanArt = thumbnail
                else:
                    fanArt = channel('fanart')[0].string
                if fanArt == None:
                    raise
            except:
                pass
            try:
                desc = channel('info')[0].string
                if desc == None:
                    raise
            except:
                desc = ''

            try:
                genre = channel('genre')[0].string
                if genre == None:
                    raise
            except:
                genre = ''

            try:
                date = channel('date')[0].string
                if date == None:
                    raise
            except:
                date = ''
            try:
                addDir(name.encode('utf-8', 'ignore'),url.encode('utf-8'),3,thumbnail,fanArt,desc,genre,date)
            except:
                print 'There was a problem adding directory - '+name.encode('utf-8', 'ignore')
        getItems(items,fanArt)
        

def getSubChannelItems(name,url,fanart):
        soup = getSoup(url)
        channel_list = soup.find('subchannel', attrs={'name' : name})
        items = channel_list('subitem')
        getItems(items,fanart)


def getItems(items,fanart):
        for item in items:
            try:
                name = item('title')[0].string
            except:
                print '--- Name Error ---'
                name = ''
            try:
                url = []
                for i in item('link'):
                    url.append(i.string)
            except:
                print '--- URL Error Passing ---'+name
                continue

            try:
                thumbnail = item('thumbnail')[0].string
                if thumbnail == None:
                    raise
            except:
                thumbnail = ''
            try:
                if not item('fanart'):
                    if addon.getSetting('use_thumb') == "true":
                        fanArt = thumbnail
                    else:
                        fanArt = fanart
                else:
                    fanArt = item('fanart')[0].string
                if fanArt == None:
                    raise
            except:
                fanArt = fanart
            try:
                desc = item('info')[0].string
                if desc == None:
                    raise
            except:
                desc = ''

            try:
                genre = item('genre')[0].string
                if genre == None:
                    raise
            except:
                genre = ''

            try:
                date = item('date')[0].string
                if date == None:
                    raise
            except:
                date = ''

            regexs = None
            if item('regex'):
                try:
                    regexs = {}
                    for i in item('regex'):
                        regexs[i('name')[0].string] = {}
                        regexs[i('name')[0].string]['expre'] = i('expres')[0].string
                        regexs[i('name')[0].string]['page'] = i('page')[0].string
                        try:
                            regexs[i('name')[0].string]['refer'] = i('referer')[0].string
                        except:
                            print "Regex: -- No Referer --"
                        try:
                            regexs[i('name')[0].string]['agent'] = i('agent')[0].string
                        except:
                            print "Regex: -- No User Agent --"
                    regexs = urllib.quote(repr(regexs))
                except:
                    regexs = None
                    print 'regex Error: '+name.encode('utf-8', 'ignore')
                
            try:
                if len(url) > 1:
                    alt = 0
                    playlist = []
                    for i in url:
                        playlist.append(i)
                    for i in url:
                        alt += 1
                        addLink(i,'%s) %s' %(str(alt), name.encode('utf-8', 'ignore')),thumbnail,fanArt,desc,genre,date,True,playlist,regexs)
                    else:
                        addLink('', name.encode('utf-8', 'ignore'),thumbnail,fanArt,desc,genre,date,True,playlist,regexs)
                else:
                    addLink(url[0],name.encode('utf-8', 'ignore'),thumbnail,fanArt,desc,genre,date,True,None,regexs)
            except:
                print 'There was a problem adding link - '+name.encode('utf-8', 'ignore')
            setView('movies', 'default')


def getRegexParsed(regexs, url):
        regexs = eval(urllib.unquote(regexs))
        cachedPages = {}
        doRegexs = re.compile('\$doregex\[([^\]]*)\]').findall(url)
        for k in doRegexs:
            if k in regexs:
                m = regexs[k]
                if m['page'] in cachedPages:
                    link = cachedPages[m['page']]
                else:
                    req = urllib2.Request(m['page'])
                    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1')
                    if 'refer' in m:
                        req.add_header('Referer', m['refer'])
                    if 'agent' in m:
                        req.add_header('User-agent', m['agent'])
                    response = urllib2.urlopen(req)
                    link = response.read()
                    response.close()
                    cachedPages[m['page']] = link
                reg = re.compile(m['expre']).search(link)
                url = url.replace("$doregex[" + k + "]", reg.group(1).strip())
        item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
            

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]
        return param


def play_playlist(name, list):
        playlist = xbmc.PlayList(1)
        playlist.clear()
        item = 0
        for i in list:
            item += 1
            info = xbmcgui.ListItem('%s) %s' %(str(item),name))
            playlist.add(i, info)
        xbmc.executebuiltin('playlist.playoffset(video,0)')


def addDir(name,url,mode,iconimage,fanart,description,genre,date,showcontext=False):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&fanart="+urllib.quote_plus(fanart)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description, "Genre": genre, "Date": date } )
        liz.setProperty( "Fanart_Image", fanart )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok


def addLink(url,name,iconimage,fanart,description,genre,date,showcontext,playlist,regexs):         
        ok = True
        if regexs: mode = '11'
        else: mode = '9'
        u=sys.argv[0]+"?"
        play_list = False
        if playlist:
            if addon.getSetting('add_playlist') == "false":
                u += "url="+urllib.quote_plus(url)+"&mode="+mode
            else:
                u += "mode=10&name=%s&playlist=%s" %(urllib.quote_plus(name), urllib.quote_plus(str(playlist).replace(',','|')))
                play_list = True
        else:
            u += "url="+urllib.quote_plus(url)+"&mode="+mode
        if regexs:
            u += "&regexs="+regexs
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": description, "Genre": genre, "Date": date } )
        liz.setProperty( "Fanart_Image", fanart )
        liz.setProperty('IsPlayable', 'true')
        if not playlist is None:
            playlist_name = name.split(') ')[1]
            contextMenu_ = [('Play '+playlist_name+' PlayList','XBMC.RunPlugin(%s?mode=10&name=%s&playlist=%s)' %(sys.argv[0], urllib.quote_plus(playlist_name), urllib.quote_plus(str(playlist).replace(',','|'))))]
            liz.addContextMenuItems(contextMenu_)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok


def setView(content, viewType):
        if content:
                xbmcplugin.setContent(int(sys.argv[1]), content)
        if addon.getSetting('auto-view') == 'true':
                xbmc.executebuiltin("Container.SetViewMode(%s)" % addon.getSetting(viewType) )


params=get_params()

url=None
name=None
mode=None
playlist=None
regexs=None

try:
    url=urllib.unquote_plus(params["url"]).decode('utf-8')
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    iconimage=urllib.unquote_plus(params["iconimage"])
except:
    pass
try:
    fanart=urllib.unquote_plus(params["fanart"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    playlist=eval(urllib.unquote_plus(params["playlist"]).replace('|',','))
except:
    pass
try:
    regexs=params["regexs"]
except:
    pass

print "Mode: "+str(mode)
if not url is None:
    print "URL: "+str(url.encode('utf-8'))
print "Name: "+str(name)


if mode==None:
    print "getData"
    getData(data, fanart)

elif mode==2:
    print "getChannelItems"
    getChannelItems(name,url,fanart)

elif mode==3:
    print ""
    getSubChannelItems(name,url,fanart)

elif mode==9:
    print "setResolvedUrl"
    item = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

elif mode==10:
    print "play_playlist"
    play_playlist(name, playlist)

elif mode==11:
    print "getRegexParsed"
    getRegexParsed(regexs, url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
