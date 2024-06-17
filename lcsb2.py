#!/home/sigma/.local/bin/python3
# -*- coding: utf-8 -*-
# LGPLv2+ license, look it up
# SPDX-License-Identifier: LGPL-2.0-or-later
# https://en.wikipedia.org/wiki/User:Lowercase_sigmabot_II/Source.py

import sys
import os
import builtins

import ceterach
import passwords

import mwparserfromhell as mwparser

builtins.print = lambda *args, **kwargs: None

def main():
    global api
    api = ceterach.api.MediaWiki("https://ko.wikipedia.org/w/api.php")
    api.login("Revibot II", passwords.lcsb2)
    api.set_token("edit")
    bot = SandBot1(api)
    bot.run()

class SandBot1:
    REINSERT = "{{이 줄은 지우지 마세요 (연습장 안내문)}}\n\n"
    SANDBOXES = {"위키백과:연습장",
    }
    TEMPLATES = {"틀:이 줄은 지우지 마세요 (얀습장 안내문)",
                 "틀:연습장 안내문",
    }

    def __init__(self, api, shutoff="User:Revibot II/Shutoff"):
        self.api = api
        self.shutoff_page = api.page(shutoff)

    @property
    def is_allowed(self):
        return self.shutoff_page.content.lower() == "true" #or True

    def check_if_heading_is_gone(self, box):
        tl = self.api.iterator(500, prop="templates", tlnamespace=10, tllimit=500, titles=box.title)
        res = {x['title'] for x in next(tl).get("templates", "")}
        return not res & self.TEMPLATES

    def run(self):
        if not self.is_allowed:
            return
        for sandbox in self.SANDBOXES:
            box = self.api.page(sandbox)
            if box.revision_user.name == "Revibot II":
                continue
            if self.check_if_heading_is_gone(box):
                box.prepend(self.REINSERT, summary="연습장 헤더 재삽입) (봇")
                print("\thad a header reinserted!")

if __name__ == "__main__":
    main()
