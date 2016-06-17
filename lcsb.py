#!/home/sigma/.local/bin/python3
# -*- coding: utf-8 -*-
# LGPLv2+ license, look it up

import re
import builtins
import traceback
from datetime import datetime, timedelta

import ceterach
import passwords

import mwparserfromhell as mwparser


def main():
    global api
    api = ceterach.api.MediaWiki("https://en.wikipedia.org/w/api.php")
    api.login("Lowercase sigmabot", passwords.lcsb)
    api.set_token("edit")
    bot = ProtectionTemplateBot(api)
    if bot.is_allowed or 1:
        bot.run()
    else:
        print("Check the bot shutoff page!")


def allow_bots(text, user):
    return not re.search(r'\{\{(nobots|bots\|(allow=none|deny=.*?' + user + r'.*?|optout=all|deny=all))\}\}', text)


#builtins.print = lambda *args, **kwargs: None


class ProtectionTemplateBot:
    REDIR_TL = "{{r protected}}"
    EDIT_TL = {"pp-dispute", "pp-vandalism", "pp-template",
               "pp-semi-sock", "pp-semi-blp", "pp-semi-indef",
               "pp-protected", "pp-office", "pp-reset",
               "pp-semi", "pp-semi-protect", "sprotect",
               "sprotected", "semiprotected", "pp-semi-prot",
               "pp-semi-vandalism", "pp-semi-protected",
               "pp-full", "pp-blp", "pp-sock",
    }
    MOVE_TL = {"pp-move-dispute", "pp-move-vandalism",
               "pp-move-indef", "pp-move", "mprotect",
               "m-protected", "mprotected2", "mpprotected"
    }
    PROT_TL = EDIT_TL | MOVE_TL | {"r protected", "r semi-protected", "r fully protected"}
    NO_PROTECTION = {'edit': (None,) * 2,
                     'create': (None,) * 2,
                     'move': (None,) * 2,
    }

    def __init__(self, api, shutoff="User:Lowercase sigmabot/Shutoff"):
        self.api = api
        self.shutoff_page = api.page(shutoff)

    @property
    def is_allowed(self):
        return self.shutoff_page.content.lower() == "true" #or True

    @property
    def protected_pages(self):
        import sys
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                yield self.api.page(arg)
            return
        for x in self.api.category("Category:Wikipedia pages with incorrect protection templates").members:
            if not x.namespace in (2, 3):
                yield x
        for x in self.api.iterator(150, list='logevents', letype='protect'):
            #The nonexistent page check will be done later.
            if x['ns'] in (2, 3):
                continue
            yield self.api.page(x['title'])

    def check_rev_stamp(self, page):
        q = {"action": "query", "prop": "revisions", "rvprop": "timestamp", "titles": page}
        res = self.api.call(**q)["query"]["pages"]
        info = tuple(res.values())[0]["revisions"][0]["timestamp"]
        stamp = datetime.strptime(info, "%Y-%m-%dT%H:%M:%SZ")
        if (datetime.utcnow() - stamp) > timedelta(seconds=15 * 60):
            return True
        return False

    def check_if_page_needs_edits(self, page):
        """"This method is a crappy hack that you should never read
        for inspiration."""
        prot_info = {k: v[0] for (k, v) in page.protection.items()}
        tls = self.get_templates_on(page)
        tl_on_page = [x.title.lower().partition(":")[2] for x in tls]
        pp_tl_on_page = self.PROT_TL.intersection(tl_on_page)
        score = 0
        for tl in pp_tl_on_page:
            if tl in self.EDIT_TL and not prot_info["edit"]:
                score += 1
            elif tl in self.MOVE_TL and not prot_info["move"]:
                score += 1
            if prot_info['edit'] and not tl in self.EDIT_TL:
                score += 1
            if prot_info['move'] and not tl in self.MOVE_TL:
                score += 1
        return score

    def build_template(self, page, **options):
        protection = mwparser.parse("{{subst:User:LikeLakers2/SWP/sync-pp}}")
        untouched_template = str(protection)
        tl = protection.filter_templates()[0]
        tl.add("small", "{{subst:User:Lowercase sigmabot/is not talk}}")
        infinity = datetime.max
        prot_info = page.protection
        prot_expiries = {k: info[1] for (k, info) in prot_info.items()}
        # processed_options = "|".join(k + "=" + v for (k, v) in options.items())
        for (k, v) in options.items():
            tl.add(k, v)
        for k in prot_expiries:
            if not prot_expiries[k]:
                continue
            if k == "edit":
                if prot_expiries[k] == infinity:
                    tl.add("expiry", "indef")
                    if page.namespace == 10:
                        tl.add("reason", "template")
                    else:
                        tl.add("reason", "long-term")
                else:
                    tl.add("expiry", str(prot_expiries[k]))
            if k == "move":
                level, expiry = prot_info[k]
                if level == "autoconfirmed":
                    continue  # Do not add pp-move for semiprotected pages
                elif level == "sysop":
                    if expiry == infinity:
                        tl.add("moveexpiry", "indef")
                        tl.add("movereason", "generic")
                    else:
                        tl.add("moveexpiry", str(expiry))
        if str(protection) == untouched_template:
            return ""
        return str(protection)

    def selectively_remove(self, page):
        print("Selective removal on {!r}".format(page.title))
        kw = {}
        prot_info = {k: v[0] for (k, v) in page.protection.items()}
        original_text = page.content
        code = mwparser.parse(page.content)
        templates = code.filter_templates()
        if page.is_redirect:
            # This method is only called if there are templates on the
            # page and the page is protected at all
            return
        # This is the selective removal part
        if not prot_info['edit']:
            for template in templates:
                tl = template.name.lower()
                if tl in self.EDIT_TL:
                    print("\tRemoving edit templates")
                    code.remove(template)
        if not prot_info['move']:
            for template in templates:
                tl = template.name.lower()
                if tl in self.MOVE_TL:
                    print("\tRemoving move templates")
                    code.remove(template)
        # This is the selective adding part
        if prot_info['edit']:
            if self.EDIT_TL & {tl.name.lower() for tl in templates}:
                kw['addedit'] = 'no'
                print("\taddedit=no")
        if prot_info['move']:
            if self.MOVE_TL & {tl.name.lower() for tl in templates}:
                kw['addmove'] = 'no'
                print("\taddmove=no")
        if len(kw) > 1:
            print("Nevermind, {!r} doesn't need edits".format(page))
            return
        text = self.build_template(page, **kw) + str(code)
        if text == original_text:
            print("Nevermind, {!r} doesn't need edits".format(page))
            return
        page.edit(text, "Correcting protection templates) (bot", minor=True, bot=True)

    def get_templates_on(self, page):
        tl = tuple(self.api.iterator(1000, prop="templates", tlnamespace=10, titles=page.title, tllimit=1000))
        if not tl[0].get("templates", None):
            return
        for x in tl[0]["templates"]:
            yield self.api.page(x["title"])

    def rm_templates(self, page):
        text = mwparser.parse(page.content)
        summ = "Removing protection templates) (bot"
        print(page.title)
        for tl in text.filter_templates():
            if tl.name.lower() in self.PROT_TL or tl.name.lower().startswith("pp-"):
                text.remove(tl)
        text = str(text)
        print("Removing templates from {!r}".format(page.title))
        return page.edit(text, summary=summ, minor=True, bot=True)

    def add_to_redir(self, page):
        templates_on_page = (x.title.partition(":")[2].lower() for x in self.get_templates_on(page))
        if "r protected" in templates_on_page:
            print("{!r} already has a redirect template".format(page.title))
            return
        print("Adding templates to redirect {!r}".format(page.title))
        return page.append(self.REDIR_TL, "Adding protection template to redirect) (bot", minor=True, bot=True)

    def add_templates(self, page):
        summary = "Adding protection templates) (bot"
        print("Adding templates to {!r}".format(page.title))
        tl = self.build_template(page)
        if not tl.strip():
            print("\tNevermind, skipping {!r}".format(page.title))
            return
        meth = page.append if page.namespace == 10 else page.prepend
        if page.content.startswith(("{|", '=')):
            tl += "\n"
        return meth(tl, summary, minor=True, bot=True)

    def run(self):
        for page in self.protected_pages:
            if not page.exists:
                print("{!r} doesn't exist.".format(page.title))
                continue
            if page.namespace == 10 or len(page.content) > 150000:
                continue
            protection = {k: v[0] for (k, v) in page.protection.items()}
            #if protection["edit"][0] == "sysop":
            if 'sysop' in str(protection['edit']):  # Bad programming :(
                print("{!r} is full protected!".format(page.title))
                continue
            templates_on_page = [x.title.partition(":")[2].lower() for x in self.get_templates_on(page)]
            has_pp_template = self.PROT_TL.intersection(templates_on_page)#"pp-meta" in templates_on_page
            if "documentation" in templates_on_page:
                print("{!r} has a doc template on it.".format(page.title))
                continue
            if not allow_bots(page.content, "Lowercase sigmabot"):
                print("{!r} does not allow the bot to edit".format(page.title))
                continue
            if page.title.lower().count("wikipedia signpost"):
                print("{!r} is the signpost.".format(page.title))
                continue
            if not self.check_rev_stamp(page.title):
                print("{!r} needs to wait until 15 minutes after most recent revision".format(page.title))
                continue
            try:
                if not has_pp_template:
                    if page.is_redirect and not "template:r protected" in templates_on_page:
                        if protection["edit"]:
                            self.add_to_redir(page)
                    else:
                        if len(page.content) > 150000:
                            print("{!r} is too long for us to safely determine the templates on the page.")
                            continue
                        self.add_templates(page)
                        #print(templates_on_page)
                else:
                    if any(protection.values()):  # Has protection and pp template
                        self.selectively_remove(page)
                    else:  # No protection, but has_pp_template
                        self.rm_templates(page)
            except Exception as e:
                print(repr(page.title), "error")
                traceback.print_exc()
                continue

if __name__ == "__main__":
    main()
    api.logout()
