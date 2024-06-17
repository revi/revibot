# -*- coding: utf-8  -*-
# License: CC BY SA 3.0 Unported / GFDL
# Source: https://ko.wikipedia.org/wiki/%EC%82%AC%EC%9A%A9%EC%9E%90:Kwanin-bot/script
# SPDX-License-Identifier: CC-BY-SA-3.0 OR GFDL-1.3-or-later

import random
import pywikibot
import catlib

def list_shuffle(list, N):
    if len(list)<=N: return list
    return random.sample(list, N)

def cat_list_rec(top_cat, ignore_cats=None):
    if ignore_cats==None: ignore_cats = []

    articlelist = [] # assume that top_cat has no article
    cat = catlib.Category(pywikibot.Site(), top_cat)
    for subcat in cat.subcategories():
        if not subcat.title() in ignore_cats:
            for page in subcat.articles():
                if not ":" in page.title():
                    articlelist.append(page.title())
    return articlelist

def cat_list(top_cat):
    cat = catlib.Category(pywikibot.Site(), top_cat)
    return [i.title() for i in cat.articles() if not ":" in i.title()]

def main():
    count = 7

    '''stub_ignore_cats = [
        u'분류:토막글 분류가 잘못된 문서',
    ]'''

    cats = [
        (u'정리 필요', u'분류:정리가 필요한 모든 글'),
        (u'POV', u'분류:중립성에 이의가 제기된 모든 문서'),
        (u'문서 등재 기준', u'분류:문서 등재 기준에 부합하는지 입증이 요구되는 모든 문서'),
        (u'독자 연구', u'분류:모든 독자 연구 의심 문서'),
        (u'세계화', u'분류:일부 지역만을 다루는 모든 글'),
        (u'외톨이', u'분류:모든 외톨이 글'),
        (u'합병', u'분류:합쳐야 할 문서'),
        (u'분할', u'분류:분할이 필요한 문서'),
        (u'이동 필요', u'분류:옮겨야 할 문서'),
        (u'번역 필요', u'분류:번역되지 않은 문장이 포함된 문서'),
        (u'기계 번역', u'분류:모든 기계 번역 의심 문서‎'),
        ]

    #stub_list = cat_list_rec(u'분류:토막글 분류', stub_ignore_cats)

    data = []

    for title, catname in cats:
        data.append((title, catname, cat_list(catname)))

    result = u""
    result += u"다음과 같은 문서들이 사용자 여러분들의 편집을 필요로 하고 있습니다.\n"
    result += u"<!-- 이 문서의 목록은 봇을 통해 자동으로 변경됩니다. -->\n"
    #result += u"""* '''[[위키백과:토막글|토막글]]''': """
    #result += u", ".join([u"[[%s]]"%i for i in list_shuffle(stub_list, count)]) + u"\n"

    for title, catname, lis in data:
        result += u"""* '''[[:%s|%s]]''': """%(catname, title)
        result += u", ".join([u"[[%s]]"%i for i in list_shuffle(lis, count)]) + u"\n"

    page = pywikibot.Page(pywikibot.Site(), u'위키백과:사용자 모임/자동목록')
    page.put(result, u"봇:자동목록 갱신")

    print (result)
    #print ("# of stubs:", len(stub_list))
    for i, m, j in data:
        print ("# of %s"%i, len(j))

if __name__ == "__main__":
    main()
