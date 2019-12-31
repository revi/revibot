from datetime import datetime, date, time
import pywikibot
from pywikibot import pagegenerators

site = pywikibot.Site('ko','wikipedia')

today = date.today()
thisyear = today.year
thismonth = today.month

if thismonth == 12:
    thisyear = today.year + 1
    thismonth = 1

nextmonth = today.month + 1

thisyear = str(thisyear)
thismonth = str(thismonth)
nextmonth = str(nextmonth)

page = pywikibot.Page(site, u"위키백과:사랑방 (기술)/"+thisyear+"년 "+nextmonth+"월")
page.text = u"<noinclude>{{위키백과:사랑방 (기술)/보존|"+thisyear+"|"+nextmonth+"}}</noinclude>"

page.save(u"월별 보존문서 사전 생성) (봇")