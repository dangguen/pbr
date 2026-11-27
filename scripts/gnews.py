# 구글뉴스 RSS 최근 1일 기사 검색. 사용: python3 scripts/gnews.py "검색어1" "검색어2" ...
import sys,urllib.request,urllib.parse,re,html,email.utils,datetime as dt
now=dt.datetime.now(dt.timezone.utc)
for q in sys.argv[1:]:
    u="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":q+" when:1d","hl":"ko","gl":"KR","ceid":"KR:ko"})
    x=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read().decode()
    print("###",q)
    for it in re.findall(r"<item>(.*?)</item>",x,re.S)[:12]:
        t=html.unescape(re.search(r"<title>(.*?)</title>",it,re.S).group(1))
        l=re.search(r"<link>(.*?)</link>",it).group(1)
        d=email.utils.parsedate_to_datetime(re.search(r"<pubDate>(.*?)</pubDate>",it).group(1))
        if (now-d).total_seconds()<36*3600: print(f"- {(d+dt.timedelta(hours=9)):%m-%d %H:%M} {t} | {l}")
