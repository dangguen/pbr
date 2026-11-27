#!/usr/bin/env python3
"""DART '오늘의 공시'를 모두 받아 밸류업·공개매수·자사주·상속·증여·지배구조 관련 공시를 골라낸다.

사용: python3 scripts/dart_daily.py [YYYY-MM-DD]   (생략 시 오늘 KST)
출력: 마크다운 표 (관심종목 해당 여부 ★ 표시)
"""
import datetime as dt
import html
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

URL = "https://dart.fss.or.kr/dsac001/search.ax"
KEYWORDS = {
    "밸류업": ["기업가치제고", "기업가치 제고"],
    "공개매수/M&A": ["공개매수", "최대주주변경", "주식양수도", "합병", "분할", "포괄적주식교환", "상장폐지"],
    "자사주": ["자기주식", "자사주", "주식소각"],
    "상속·증여/지분": ["최대주주등소유주식변동", "상속", "증여", "주식등의대량보유", "임원ㆍ주요주주특정증권"],
    "배당/주주환원": ["현금ㆍ현물배당", "주주환원"],
}
EXCLUDE = ["집합투자", "투자신탁", "투자회사"]
ROW = re.compile(
    r'<td[^>]*>\s*(\d{2}:\d{2})\s*</td>.*?title="([^"]+?) 기업개황.*?rcpNo=(\d+)".*?title="([^"]+?) 공시뷰어',
    re.S,
)


def fetch(date: str, page: int) -> str:
    data = urllib.parse.urlencode(
        {"selectDate": date, "pageGrouping": "A", "currentPage": page, "maxResults": 100}
    ).encode()
    req = urllib.request.Request(URL, data=data, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode("utf-8", "replace")


def watchlist() -> set:
    p = Path(__file__).resolve().parent.parent / "저PBR_151_관심종목.md"
    names = set()
    for line in p.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*([^|]+?)\s*\|", line)
        if m and m.group(1) not in ("기업", "---"):
            names.add(m.group(1))
    return names


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else (
        dt.datetime.utcnow() + dt.timedelta(hours=9)).strftime("%Y-%m-%d")
    date = day.replace("-", ".")
    first = fetch(date, 1)
    m = re.search(r"\[1/(\d+)\]", first)
    pages = int(m.group(1)) if m else 1
    rows = ROW.findall(first)
    for p in range(2, pages + 1):
        rows += ROW.findall(fetch(date, p))
    wl = watchlist()
    hits = []
    for t, corp, rcp, title in rows:
        corp, title = html.unescape(corp).strip(), html.unescape(title).strip()
        if any(x in title for x in EXCLUDE):
            continue
        for cat, kws in KEYWORDS.items():
            if any(k in title for k in kws):
                hits.append((cat, corp in wl, t, corp, title, rcp))
                break
    hits.sort(key=lambda h: (not h[1], list(KEYWORDS).index(h[0]), h[2]))
    print(f"## DART 공시 ({day}) — 전체 {len(rows)}건 중 관련 {len(hits)}건 (★=관심종목)\n")
    print("| 구분 | 시간 | 회사 | 보고서명 | 링크 |\n|---|---|---|---|---|")
    for cat, star, t, corp, title, rcp in hits:
        print(f"| {cat} | {t} | {'★ ' if star else ''}{corp} | {title} | "
              f"[원문](https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp}) |")


if __name__ == "__main__":
    main()
