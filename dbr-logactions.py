#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import pywikibot
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

pywikibot.output(u'\nScript started.')

import MySQLdb
conn = MySQLdb.connect(
    read_default_file = "/data/project/revibot-ii/replica.my.cnf",
    host = "kowiki.analytics.db.svc.eqiad.wmflabs",
    db = "kowiki_p",
)

# -------------------- Header -------------------- #
pywikibot.output(u'\nLoding header...')

text = '{{단축|백:기록목록}}\n[[특:기록|공개 기록]]별 사용자 목록입니다. 마지막 갱신 <onlyinclude>~~~~~</onlyinclude>.\n__TOC__\n\n'

# -------------------- QUERY 1 - Deletions -------------------- #
pywikibot.output(u'\nDoing query 1...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'delete'
AND log_action = 'delete'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 삭제 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 2 - Undeletions -------------------- #
pywikibot.output(u'\nDoing query 2...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'delete'
AND log_action = 'restore'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 되살리기 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 3 - Revision deletions -------------------- #
pywikibot.output(u'\nDoing query 3...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'delete'
AND log_action = 'revision'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 특정판 삭제 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 4 - Event deletions -------------------- #
pywikibot.output(u'\nDoing query 4...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'delete'
AND log_action = 'event'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 기록 삭제 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 5 - Protections -------------------- #
pywikibot.output(u'\nDoing query 5...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'protect'
AND log_action = 'protect'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 보호 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 6 - Unprotections -------------------- #
pywikibot.output(u'\nDoing query 6...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'protect'
AND log_action = 'unprotect'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 보호 해제 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 7 - Protection modifications -------------------- #
pywikibot.output(u'\nDoing query 7...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'protect'
AND log_action = 'modify'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 보호 수정 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 8 - Blocks -------------------- #
pywikibot.output(u'\nDoing query 8...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'block'
AND log_action = 'block'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 차단 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 9 - Unblocks -------------------- #
pywikibot.output(u'\nDoing query 9...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'block'
AND log_action = 'unblock'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 차단 해제 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 10 - Block modifications -------------------- #
pywikibot.output(u'\nDoing query 10...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'block'
AND log_action = 'reblock'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 차단 수정 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!차단 수정\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 11 - User renames -------------------- #
pywikibot.output(u'\nDoing query 11...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'renameuser'
AND log_action = 'renameuser'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 사용자 이름 바꾸기 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 12 - User rights modifications -------------------- #
pywikibot.output(u'\nDoing query 12...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'rights'
AND log_action = 'rights'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 사용자 권한 바꾸기 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 13 - Whitelistings -------------------- #
# global block whitelisting
pywikibot.output(u'\nDoing query 13...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'gblblock'
AND log_action = 'whitelist'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 전역 차단 화이트리스트 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 14 - De-whitelistings -------------------- #
pywikibot.output(u'\nDoing query 14...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'gblblock'
AND log_action = 'dwhitelist'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 전역 차단 화이트리스트 해제 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'


# -------------------- QUERY 15 - AbuseFilter modifications -------------------- #
pywikibot.output(u'\nDoing query 15...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'abusefilter'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 편집 필터 수정 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'


# -------------------- QUERY 16 - History mergings -------------------- #
pywikibot.output(u'\nDoing query 16...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'merge'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 역사 합치기 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 17 - Imports -------------------- #
pywikibot.output(u'\nDoing query 17...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'import'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 가져오기 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 18 - Tag management -------------------- #
pywikibot.output(u'\nDoing query 18...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'managetags'
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 태그 관리 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- QUERY 19 - Mass messages -------------------- #
pywikibot.output(u'\nDoing query 19...')

cursor = conn.cursor()
cursor.execute("""SELECT
user_name AS user,
COUNT(log_timestamp) AS  ucount
FROM logging
JOIN user
ON user_id = log_user
WHERE log_type = 'massmessage'
AND user_name NOT IN ('MediaWiki message delivery')
GROUP BY log_user
ORDER by ucount DESC;""")

text += u'== 대량메시지 발송 ==\n'
text += u'{| class="wikitable sortable" style="width:23em;"\n|- style="white-space:nowrap;"\n!사용자\n!횟수\n'

for user, ucont in cursor.fetchall():
    text += u'|-\n'
    text += u'| [[User:%s|%s]]\n' %(user.decode("utf-8"),user.decode("utf-8"))
    text += u'| %d\n' %(ucont)
cursor.close()
text += u'|}\n'

# -------------------- UPLOAD LOGS -------------------- #
# pywikibot.output(u'\nUpload log stats information...')
#
# text += u'== Upload log ==\n'
# text += u'See [[Commons:Database reports/Upload log stats]]\n'
# 
# -------------------- END QUERYS -------------------- #
pywikibot.output(u'\nPublishing page now...\n')

site = pywikibot.Site()
page = pywikibot.Page(site, "위키백과:데이터베이스 보고서/공개 기록별 사용자 목록")
page.put(text, comment=u'데이터베이스 보고서 업데이트) (봇')


cursor.close()
conn.close()