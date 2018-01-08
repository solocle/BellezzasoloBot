import pywikibot
import ipaddress
import datetime
import time
import shelve
from pywikibot import pagegenerators

site = pywikibot.Site()
mypage = pywikibot.Page(site, u"User:Bellezzasolo Bot/Pings")
count = 0
runtracker = shelve.open("RunTrack", writeback=True)
if 'lastrun' not in runtracker:
    runtracker['lastrun'] = datetime.datetime.utcnow()-datetime.timedelta(minutes=30)
if runtracker['lastrun'] < datetime.datetime.utcnow()-datetime.timedelta(hours=24):
    runtracker['lastrun'] = datetime.datetime.utcnow()-datetime.timedelta(hours=24)
while True:
    gen = pagegenerators.RecentChangesPageGenerator(namespaces=[1,3,5,7,9,11,13,15,101,109,\
                                                                119,829])
    currun = datetime.datetime.utcnow()
    print("last run: {0}".format(runtracker['lastrun']))
    for page in gen:
        try:
            if page.editTime() < runtracker['lastrun']:
                #OK, we've checked this before or it is too old
                print("Run completed, sleeping")
                time.sleep(60)
                runtracker['lastrun'] = currun
                break
        except:
            #Problem with page, may be deleted
            continue
        for template in page.templatesWithParams():
            #print(template[0]._link.canonical_title())
            if template[0]._link.canonical_title()[9:].lower() in ["echo","replyto","ping", "reply to", "re",\
                                       "mention", "reply-to", "yo", "rto", "tping",
                                       "tiny ping", "nudge"]:
                for user in template[1]:
                    try:
                        ipaddress.ip_address(user)
                        #OK, this is an IP
                        #Check to see if ping is in old revision
                        therevision = None
                        for rev in page.revisions():
                            hist = rev.hist_entry()
                            therevision = hist.revid
                            if hist.timestamp < runtracker['lastrun']:
                                break
                        comparison = site.compare(therevision, page.latest_revision_id)
                        comparator = pywikibot.diff.html_comparator(comparison)
                        user_found = False
                        for entry in comparator['added-context']:
                            if user in entry:
                                user_found = True
                        if not user_found:
                            raise ValueError
                        userpage = "User talk:%s"%user
                        #Now open IP talk page
                        talkpage = pywikibot.Page(site,userpage)
                        foundTalkback = False
                        for templ in talkpage.templatesWithParams():
                            template_test_name = templ[0]._link.canonical_title()
                            if template_test_name[9:].lower() in ["talkback", "talkbacktiny", "wb",\
                                                        "whisperback", "no talkback", "bots"]:
                                foundTalkback = True
                                break
                        if foundTalkback:
                            continue
                        if "<!-- [[Template:Please see]] -->" in talkpage.text:
                            continue
                        canon_title = page._link.canonical_title()
                        print(canon_title)
                        mypage.text += u"\n*[[%s]] - %s"%\
                                   (userpage,page._link.canonical_title())
                        #print(talkpage.text)
                        talkpage.text += u"{{ subst:Please see | %s }}<br />\n\
    I am an experimental bot, this may be in error<br />\n"%(canon_title)
                        mypage.save(u"Found IP reply")
                        talkpage.save(u"Notifying you of talk page edit in response to you")
                        count += 1
                        if count == 3:
                            exit()
                    except ValueError as e:
                        pass
