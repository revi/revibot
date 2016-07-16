#!/usr/bin/python
# -*- coding: utf-8 -*-
# This script is not licensed under LICENSE file and is ALL RIGHT RESERVED.

import pywikibot

import MySQLdb
conn = MySQLdb.connect(
    read_default_file = "/data/project/revibot/replica.my.cnf",
    host = "kowiki.labsdb",
    db = "kowiki_p",
)

cursor = conn.cursor()
cursor.execute("""SELECT
 ipb_address AS buser,
 DATE_FORMAT(ipb_expiry, "%b %d %Y %h:%i %p") as edate,
 ipb_by_text AS admin,
 ipb_reason AS reason
FROM ipblocks
WHERE ipb_expiry < DATE_FORMAT(DATE_ADD(NOW(), INTERVAL +3 DAY), "%Y%m%d%H%i%s")
AND ipb_expiry NOT LIKE "%infinity%"
AND ipb_address IS NOT NULL;""")

text = '{{/intro|~~~~~}}\n\n'

text += u'{| class="wikitable sortable plainlinks" style="width:100%; margin:auto;"\n'
text += u'|- style="white-space:nowrap;"\n'
text += u'! 사용자\n'
text += u'! 만료 시간\n'
text += u'! 차단한 관리자\n'
text += u'! 사유\n'

for buser, edate, admin, reason in cursor.fetchall():
    text += u'|-\n'
    text += u'| {{사용자 링크|%s}}\n' %(buser.decode("utf-8"))
    text += u'| %s\n' %(edate.decode("utf-8"))
    text += u'| [[User:%s|%s]]\n' %(admin.decode("utf-8"),admin.decode("utf-8"))
    text += u'| <nowiki>%s</nowiki>\n' %(reason.decode("utf-8"))

text += u'|}\n\n'
text += u'== See also ==\n'
text += u'* [[Special:BlockList]]\n'
text += u'* [[Special:Log/block]]\n'

site = pywikibot.Site()
page = pywikibot.Page(site, "User:Revibot II/Unblock")
page.put(text, comment=u'봇: 업데이트.')

cursor.close()
conn.close()
