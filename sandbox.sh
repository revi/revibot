#!/bin/bash
# Basic shell script for Revibot II sandbox cleaning
# This script is free software; licensed under GPLv3 or later.
# Login is handled by BotPassword.

cd core # Go to pywikibot core
python pwb.py clean_sandbox -delay:5 # Actual scripts - clean the sandbox.