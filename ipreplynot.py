import pywikibot
import ipaddress
from pywikibot import pagegenerators

site = pywikibot.Site()
mypage = pywikibot.Page(site, u"User:Bellezzasolo Bot/Pings")
gen = pagegenerators.RecentChangesPageGenerator(namespaces=[1,3,5,7,9,11,13,15,101,109,119,829])
count = 0
for page in gen:
    #Do something with the page object, for example:
    text = page.text.lower()
    for template in page.templatesWithParams():
        #print(template[0]._link.canonical_title())
        if template[0]._link.canonical_title()[9:].lower() in ["echo","replyto","ping", "reply to", "re",\
                                   "mention", "reply-to", "yo", "rto", "tping",
                                   "tiny ping", "nudge"]:
            for user in template[1]:
                try:
                    ipaddress.ip_address(user)
                    #OK, this is an IP
                    userpage = "User talk:%s"%user
                    #Now open IP talk page
                    talkpage = pywikibot.Page(site,userpage)
                    foundTalkback = False
                    for templ in talkpage.templatesWithParams():
                        template_test_name = templ[0]._link.canonical_title()
                        if template_test_name[9:].lower() in ["talkback", "talkbacktiny", "wb",\
                                                    "whisperback", "no talkback"]:
                            foundTalkback = True
                            break
                    if foundTalkback:
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
                    if count == 1:
                        exit()
                except ValueError as e:
                    pass
