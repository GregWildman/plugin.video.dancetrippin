import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmcaddon, os, json
from time import strftime

__settings__ = xbmcaddon.Addon(id='plugin.video.dancetrippin')
__language__ = __settings__.getLocalizedString

def CATEGORIES():
    # List all the sessions.
    sessions = {}

    # Episodes
    sessions[__language__(30001)] = {
        'feed': 'http://www.dancetrippin.tv/video/list/dj',
        'image': os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'episodes.jpg'),
        'plot':  '',
        'genre': 'Electonic',
        'count': 0
    }

    # SOL Sessions
    sessions[__language__(30002)] = {
        'feed': 'http://www.dancetrippin.tv/video/list/sol',
        'image': os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'sol.jpg'),
        'plot': '',
        'genre': 'Electonic'
    }

    # Ibiza Global Radio
    sessions[__language__(30003)] = {
        'feed': 'http://www.dancetrippin.tv/video/list/igr',
        'image': os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'igr.jpg'),
        'plot': '',
        'genre': 'Electonic'
    }

    # Other videos
    sessions[__language__(30004)] = {
        'feed': 'http://www.dancetrippin.tv/video/list/other',
        'image': os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'other.jpg'),
        'plot': '',
        'genre': 'Electonic'
    }

    # Loop through each of the sessions and add them as directories.
    x = 2
    quality = int(__settings__.getSetting("video_quality"))
    for name, data in sessions.iteritems():
        # @TODO Get the ordering correct.
        data['count'] = x
        x = x + 1
        addDir(name, data['feed'], 1, data['image'], data)

def INDEX(name, url, page):
    # Load the JSON feed.
    req = urllib2.Request(url)
    req.add_header('User-Agent', "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8")
    data = urllib2.urlopen(req)

    # Parse the data
    dj_data = json.load(data)
    count = 1

    # Figure out where to start and where to stop the pagination.
    # TODO: Fix the Episodes per Page setting.
    episodesperpage = 25 # int(__settings__.getSetting("episodes_per_page"))
    start = episodesperpage * int(page);
    print "Episodes per Page: " + str(episodesperpage) + "\n"
    print "Start:" + str(start);
    n = 0;

    # Wrap in a try/catch to protect from broken JSON feeds.
#    try:
    for item in dj_data:
        # Set up the pagination properly.
        n += 1
        if (n < start):
            # Skip this episode since it's before the page starts.
            continue
        if (n >= start + episodesperpage):
            # Add a go to next page link, and skip the rest of the loop.
            addDir(
                name = __language__(30300),
                url = url,
                mode= 1,
                iconimage = os.path.join(__settings__.getAddonInfo('path'), 'resources', 'media', 'next.png'),
                info = {},
                page = page + 1
            )
            break

        # Load up the initial episode information.
        info = {}
        title = item['title']
        number = item['number']
        info['title'] = str(number) + '. '
        #info['title'] = str(n) + '. '
        if (title):
            info['title'] += title
        info['tvshowtitle'] = name
        info['count'] = count
        count += 1 # Increment the show count.

        # Get the actual video. We take a time knock here as we need to hit the web again to get
        # the real video link.
        video = "http://www.dancetrippin.tv/video/embed/" + item['slug']

        # Date
        date = ''

        # Plot.
        description = item['description']
        if (description != None):
            # Attempt to strip the HTML tags.
            try:
                info['plot'] = re.sub(r'<[^>]*?>', '', description)
            except:
                info['plot'] = description

        # Author/Director.
        author = item['dj']
        if (author != None):
            info['cast'] = author

        # Load the self-closing media:thumbnail data.
        thumbnail = ''
        mediathumbnail = "http://www.dancetrippin.tv/media/" + item['image']
        if (mediathumbnail):
            thumbnail = mediathumbnail

        # Add the episode link.
        addLink(info['title'], video, date, thumbnail, info)
#    except:
#       pass

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

# Info takes Plot, date, size
def addLink(name, url, date, iconimage, info):
        ok=True
        liz=xbmcgui.ListItem(name, date, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo( type="video", infoLabels=info )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name, url, mode, iconimage, info, page = 0):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name) + "&page="+str(page)
    ok=True
    info["Title"] = name
    liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo(type="video", infoLabels=info)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

params = get_params()
url = None
name = None
mode = None
page = None

try:
        url = urllib.unquote_plus(params["url"])
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode = int(params["mode"])
except:
        pass
try:
        page = int(params["page"])
except:
        page = 0

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Page: "+str(page)

if mode==None or url==None or len(url)<1:
        CATEGORIES()
elif mode==1:
        INDEX(name, url, page)

print "XX: we are here :" + str(url) + ":"
xbmcplugin.endOfDirectory(int(sys.argv[1]))

