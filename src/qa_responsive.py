"""Responsive layout checks. Media queries need a real browser, so this suite is
Playwright-based rather than jsdom. Run: python3 qa_responsive.py"""
from playwright.sync_api import sync_playwright
import os, sys
cwd=os.getcwd(); P=F=0
def t(n,ok):
    global P,F
    if ok: P+=1; print('  ok   '+n)
    else:  F+=1; print('  FAIL '+n)

with sync_playwright() as p:
    b=p.chromium.launch()
    def page(w,h=1000):
        pg=b.new_page(viewport={'width':w,'height':h})
        pg.goto('file://'+cwd+'/index.html')
        return pg

    # --- desktop ---
    pg=page(1800); pg.evaluate('setPmMode(true); go("home")'); pg.wait_for_timeout(400)
    t('desktop: wrap widens past 1120', pg.evaluate('document.querySelector(".wrap").getBoundingClientRect().width')>1200)
    t('desktop: PM hero is a grid', pg.evaluate('getComputedStyle(document.querySelector(".hero .wrap")).display')=='grid')
    em=pg.evaluate('document.querySelector(".pm-hero-emblem").getBoundingClientRect()')
    h1=pg.evaluate('document.querySelector(".hero h1").getBoundingClientRect()')
    t('desktop: emblem and copy side by side', h1['x']>em['x']+em['width']-20)
    lede=pg.evaluate('document.querySelector(".hero .lede").getBoundingClientRect()')
    t('desktop: lede in the right column with h1', abs(lede['x']-h1['x'])<2)
    t('desktop: no horizontal overflow', pg.evaluate('document.documentElement.scrollWidth')<=1802)
    for v,sel,minc in [('pmhub','.secdir',3),('pmdiagnose','.dxlist',2),('pmvisit','.vsecs',2),('origins','.origrid',4)]:
        pg.evaluate(f'go("{v}")'); pg.wait_for_timeout(250)
        c=pg.evaluate(f'getComputedStyle(document.querySelector("{sel}")).gridTemplateColumns').count('px')
        t(f'desktop: {v} uses >={minc} columns', c>=minc)
    pg.close()

    # --- tablet ---
    pg=page(900); pg.evaluate('setPmMode(true); go("home")'); pg.wait_for_timeout(400)
    t('tablet: no overflow', pg.evaluate('document.documentElement.scrollWidth')<=902)
    pg.close()

    # --- phone ---
    pg=page(420); pg.evaluate('setPmMode(true); go("home")'); pg.wait_for_timeout(400)
    t('phone: hero not forced to 2 cols', pg.evaluate('getComputedStyle(document.querySelector(".hero .wrap")).display')!='grid')
    t('phone: no overflow', pg.evaluate('document.documentElement.scrollWidth')<=422)
    for v in ['pmhub','pmquality','pmdiagnose','pmvisit','pmfresh','pmmenucoffee','origins']:
        pg.evaluate(f'go("{v}")'); pg.wait_for_timeout(200)
        t(f'phone: {v} no overflow', pg.evaluate('document.documentElement.scrollWidth')<=422)
    pg.close()

    # --- neutral desktop unaffected ---
    pg=page(1800); pg.evaluate('go("home")'); pg.wait_for_timeout(400)
    t('neutral desktop: hero not a PM grid', pg.evaluate('getComputedStyle(document.querySelector(".hero .wrap")).display')!='grid')
    t('no bar mode button anywhere', pg.evaluate('!document.getElementById("barmodebtn")'))
    pg.close()
    b.close()

print(f'\n{P} passed, {F} failed')
sys.exit(1 if F else 0)
