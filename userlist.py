#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# Generate Userlist report
# Author:Fæ
# Date: 2014-11
# Updates
	2016-02
	Adapted to use multiple SQL connections to avoid time-out problems
	after the WMF decided to delete a critical table
	2016-05
	Move to pywikibot-core after WMF decided to stop supporting http redirection
# CC-BY-SA-4.0
"""
status = "Almost full working again, query takes an awfully long time to run. A WMF decision at the end of 2015 to delete table ''user_daily_contribs'' forced a significant rewrite of the queries behind this report, meaning it can take hours and many queries rather than taking seconds to produce. See ([[Phab:T115711]])."

import urllib, re, time, pywikibot
import MySQLdb
from datetime import date
from datetime import datetime

start=time.time()
[y,m,d] = time.strftime('%Y-%m-%d').split('-')
now = date(int(y),int(m),int(d))

# Get OTRS access list for Commons
# https://commons.wikimedia.org/wiki/Commons:OTRS/List_of_members_by_language

conn = MySQLdb.connect(
	read_default_file = "~/replica.my.cnf",
    host = "kowiki.analytics.db.svc.eqiad.wmflabs",
    db = "kowiki_p",
)

# list of users with more than 100,000 edits and active in last 180 days
query="""
SELECT user_name,
	user_editcount AS editcount,
	user_registration AS reg,
	(SELECT rev_timestamp from revision_userindex where rev_user = user_id AND rev_timestamp > DATE_ADD(NOW(), INTERVAL -180 DAY) ORDER BY rev_timestamp IS NULL, rev_timestamp DESC LIMIT 1) AS last_edit,
	user_id
FROM user u
WHERE user_editcount>={} AND user_editcount<{}
HAVING last_edit IS NOT NULL;"""

cursor = conn.cursor()

redits = [10000, 11000, 12000, 13000, 14000, 15000, 17000, 19000, 21000, 25000,
	29000, 33000, 37000, 41000, 45000, 50000,
	55000, 60000, 65000, 70000, 80000, 90000,
	100000, 110000, 120000, 140000, 160000, 180000 
	]
for r in range(200000, 10050000, 50000):
	redits.append(r)

# testing
# redits = [20000, 22000, 25000]

table = []

for r in range(len(redits)-1):
	cursor.execute(query.format(redits[r], redits[r+1]))
	for user, editcount, reg, last_edit, user_id in cursor.fetchall():
		if reg=="NULL":
			reg = 'NA'
		group = ""
		block = None
		groups=[]
		block=""
		table.append([user, int(editcount), last_edit[0:8], '.'.join(groups), str(reg)[0:4], block, user_id])

query = """
SELECT 
	GROUP_CONCAT(DISTINCT ug_group SEPARATOR ' ') AS groups,
	CONCAT(ipb_expiry, ' &mdash; ', ipb_reason) AS block
FROM user_groups
LEFT JOIN ipblocks ON ipb_user=ug_user
WHERE ug_user = {}
GROUP BY ug_user;
"""

for i in range(0, len(table)):
	row = table[i]
	cursor.execute(query.format(row[-1]))
	for group, block in cursor.fetchall():
		groups = []
		for g in ['sysop', 'bot', 'bureaucrat', 'interface-admin', 'oversight', 'checkuser',]:
				if re.search(g, str(group)): groups.append(g)
		if block=="NULL" or block is None:
				block=""
		else:
				if re.search("\d{14}", block):
						bdate=re.search("\d{14}", block).group()
						if bdate is not None and bdate!='None':
								bdate=datetime.strptime(bdate, "%Y%m%d%H%M%S").strftime("%A %d %B %Y, %H:%M")
								block=re.sub("\d{14}", bdate, block)
		table[i][3] = '.'.join(groups)
		table[i][5] = block

#table sort by second item, editcount
table = sorted(table, key = lambda e: e[1], reverse=True)


# Admins with low activity
query="""
SELECT
	user_name AS Name,
	SUM(IF(dc.day>DATE_FORMAT(DATE_ADD(NOW(), INTERVAL -365 DAY), "%Y-%m-%d"), dc.contribs, 0)) AS 12months,
	SUM(IF(dc.day>DATE_FORMAT(DATE_ADD(NOW(), INTERVAL -830 DAY), "%Y-%m-%d"), dc.contribs, 0)) AS 24months,
	GROUP_CONCAT(DISTINCT g.ug_group SEPARATOR ', ') AS groups,
	LEFT(user_registration,4) AS reg,
	user_editcount AS Total
FROM user u
INNER JOIN user_groups g ON u.user_id=g.ug_user
LEFT JOIN user_daily_contribs dc ON u.user_id=dc.user_id
WHERE
	g.ug_group IN ('sysop','checkuser','bureaucrat','OTRS-member')
	AND (SELECT count(*) from user_groups gg WHERE u.user_id=gg.ug_user AND gg.ug_group='sysop')=1
GROUP BY user_name
HAVING 12months<100 AND 24months<200
ORDER BY 12months;
"""
#cursor.execute(query)
'''table_admins=[]
for user, yearone, yeartwo, grps, reg, total in cursor.fetchall():
		table_admins.append([user, int(yearone), int(yeartwo), grps, str(reg), int(total)])'''

report="{{anchor|top}}\n{|class='wikitable sortable'\n!#!!User!!Edit count!!Last edit!!Groups!!Reg"
breport="{{anchor|bots}}\n{|class='wikitable sortable' style='background:lightblue;'\n!#!!User!!Edit count!!Last edit!!Groups!!Reg"
oreport="\n{{anchor|lostusers}}\n{|class='wikitable sortable' style='background:lightyellow;'\n!#!!User!!Edit count!!Last edit!!Groups!!Reg\n|+Users with more than 10,000 edits inactive for more than 30 days (and less than 180)"
count=0;bcount=0;ocount=0
# 0 User
# 1 Edit count
# 2 Last edit
# 3 [Groups]
# 4 Reg
# 5 Block
for row in table:
		if row[2] is None:
			continue
		[y,m,d]=[row[2][0:4], row[2][4:6], row[2][6:8]]
		ledate = date(int(float(y)),int(float(m)),int(float(d)))
		daysago= (now-ledate).days
		rowtext ="\n|-\n| {0:0>4} "
		# User
		if row[5]=="" or row[5] is None:
				rowtext+="|| "+row[0].decode('utf-8')
		else:
				rowtext+="|| <abbr title='Account blocked until "+row[5]+"' style='color:red;'>"+row[0].decode('utf-8')+"</abbr>"
		rowtext+=" <small style='float:right'>[[Special:CentralAuth/"+re.sub(" ","_", row[0].decode('utf-8'))+"|GAM]]</small>"
		# Edit count
		rowtext+="||align=right|{:,}".format(row[1])
		# Last edit
		rowtext+="||align=center| "+row[2]+" "
		# Groups ['sysop', 'bot', 'bureaucrat', 'oversight', 'checkuser']
		rowtext+="||align=center|"
		if re.search('bot', row[3]): rowtext+='<abbr title="Bot flag" style="color:blue">#</abbr>'
		if re.search('bureaucrat', row[3]):
				rowtext+='<abbr title="Bureaucrat" style="color:red">B</abbr>'
		elif re.search('sysop', row[3]):
				rowtext+='<abbr title="Administrator" style="color:green">A</abbr>'
		else:
				rowtext+=' '
		if re.search('oversight', row[3]): rowtext+='<abbr title="Oversight" style="color:blue">O</abbr>'
		if re.search('checkuser', row[3]): rowtext+='<abbr title="Translation admin" style="color:blue">C</abbr>'

		if row[4]=="None":
				rowtext+="||align=center|<div style='color:silver'>"+row[4]+"</div>"
		else:
				rowtext+="||align=center|"+row[4]
		if daysago>30:
				if daysago<=180:
						ocount+=1
						rowtext=rowtext.format(ocount)
						oreport+=rowtext
		elif re.search("bot", row[3]) or re.search("[\s\-]bot|\bbot|bot\b|Bot| AWB|Delinker|Wikimedia Commons",row[0]):
				bcount+=1
				rowtext=rowtext.format(bcount)
				breport+=rowtext
		else:
				count+=1
				rowtext=rowtext.format(count)
				report+=rowtext
report+="\n|}"
breport+="\n|}"
oreport+="\n|}"
areport = ""

hreport=u'''{{User:Revibot/list}}
Report last updated on {{REVISIONYEAR}}-{{REVISIONMONTH}}-{{REVISIONDAY}}

Total number of [[#top|users active]] in the last 30 days on Korean  with more than 10,000 edits is ''' + "{:,d}".format(count) + ''', there are [[#bots|''' + str(bcount) + ''' active bots]] and ''' + str(ocount) +''' [[#lostusers|recently inactive users]].<!--and [[#admins|? administrators]] with low activity over two years.-->
'''


end=time.time()-start
endh=int(end/3600)
if endh>0:
	endh = str(endh) + " h "
else:
	endh = ""
endm=int(end/60) % 60
ends=end % 60
if endm>0:
		endm=str(endm)+" m "
else:
		endm=""
endline=u"Report completed: "+time.strftime("%a, %d %b %Y %H:%M")+u" ("+endh + endm+"{:0.1f}".format(ends)+" s runtime)."
endline += "\n\nStatus: "+status
endline=("\n<small>"+endline+"</small>").encode('utf-8')

site=pywikibot.Site()
out=pywikibot.Page(site, u"User:Revibot/Userlist")
pywikibot.setAction("Update report with {:,} active users".format(count))
out.put(hreport+report+'\n\n'+oreport+'\n\n'+breport+'\n\n'+areport+endline)