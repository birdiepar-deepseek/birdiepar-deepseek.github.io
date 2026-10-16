from pathlib import Path
from bs4 import BeautifulSoup as BS
from datetime import datetime
import re,json,argparse,sys

SECTIONS=('research-notes','working-papers','essays')

def parse_date(value):
    value=value.strip()
    for fmt in ('%Y-%m-%d','%B %d, %Y','%B %Y','%Y-%m','%Y'):
        try:
            date=datetime.strptime(value,fmt)
            if fmt in ('%Y-%m-%d','%B %d, %Y'):
                return date.strftime('%Y-%m-%d'),f'{date:%B} {date.day}, {date.year}'
            if fmt in ('%B %Y','%Y-%m'):return date.strftime('%Y-%m'),date.strftime('%B %Y')
            return date.strftime('%Y'),date.strftime('%Y')
        except ValueError:pass
    raise ValueError('Unsupported publication date: '+value)

def time_tag(value):
    iso,label=parse_date(value)
    return f'<time datetime="{iso}">{label}</time>'

def sync(write=False):
    changes={}; page_count=0; card_count=0; authors={}; bodies={}
    for section in SECTIONS:
        index_path=Path(section)/'index.html'; index_text=index_path.read_text(); index=BS(index_text,'html.parser')
        for card in index.select('.research-note-card, .working-paper-card'):
            route=card.select_one('a.paper-link')['href']; path=Path(route.lstrip('/'))
            if route.endswith('/'):path=path/'index.html'
            text=changes.get(path,path.read_text()); page=BS(text,'html.parser')
            details={dt.get_text(strip=True):dt.find_next_sibling('dd').get_text(' ',strip=True) for dt in page.select('dt') if dt.find_next_sibling('dd')}
            published=details.get('Published',details.get('Date'))
            assert published,route
            updated=details.get('Updated',details.get('Revised'))
            # An explicit later article-modified date is also an established source.
            modified=page.find('meta',property='article:modified_time')
            if not updated and modified:
                candidate=parse_date(modified['content'])[0]; origin=parse_date(published)[0]
                # Avoid inventing a change when precision differs or the dates match.
                if len(candidate)==len(origin) and candidate>origin:updated=modified['content']
            if updated:
                assert parse_date(updated)[0]>=parse_date(published)[0],route
            if path not in authors:
                authors[path]=details.get('Author',details.get('Authors'))
                assert authors[path],route
                body=page.select_one('.note-body, .paper-abstract-copy')
                bodies[path]=str(body)
                page_count+=1
            text,n=re.subn(r'<dt>\s*(?:Date|Published)\s*</dt>\s*<dd>.*?</dd>',lambda m:'<dt>Published</dt>\n              <dd>'+time_tag(published)+'</dd>',text,count=1,flags=re.S)
            assert n==1,route
            if updated and parse_date(updated)[0]!=parse_date(published)[0]:
                if re.search(r'<dt>\s*(?:Updated|Revised)\s*</dt>',text):
                    text=re.sub(r'<dt>\s*(?:Updated|Revised)\s*</dt>\s*<dd>.*?</dd>',lambda m:'<dt>Updated</dt>\n              <dd>'+time_tag(updated)+'</dd>',text,count=1,flags=re.S)
                else:
                    text=re.sub(r'(<dt>Published</dt>\s*<dd>.*?</dd>\s*</div>)',lambda m:m[1]+'\n            <div><dt>Updated</dt>\n              <dd>'+time_tag(updated)+'</dd></div>',text,count=1,flags=re.S)
            # Keep existing machine-readable publication dates aligned with the visible date.
            for prop,value in [('article:published_time',published),('article:modified_time',updated or published)]:
                text=re.sub(r'(<meta property="'+prop+r'" content=")[^"]*(")',lambda m:m[1]+parse_date(value)[0]+m[2],text)
            def schema(match):
                data=json.loads(match[2])
                if 'datePublished' in data:data['datePublished']=parse_date(published)[0]
                if 'dateModified' in data:data['dateModified']=parse_date(updated or published)[0]
                # Preserve the original formatting if the values already match.
                if data==json.loads(match[2]):return match[0]
                return match[1]+json.dumps(data,ensure_ascii=False,separators=(',',':'))+match[3]
            text=re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)',schema,text,flags=re.S)
            changes[path]=text
            old=card.select_one('.note-type'); kind=old.get_text(' ',strip=True).split('·')[0].strip()
            label=kind+' &middot; Published '+time_tag(published)
            if updated and parse_date(updated)[0]!=parse_date(published)[0]:label+=' &middot; Updated '+time_tag(updated)
            # Edit only the card's metadata line, preserving its title, summary, and links.
            def replace_card(match):
                c=BS(match[0],'html.parser')
                link=c.select_one('a.paper-link')
                if not link or link['href']!=route:return match[0]
                return re.sub(r'(<p class="note-type">).*?(</p>)',lambda m:m[1]+label+m[2],match[0],count=1,flags=re.S)
            index_text=re.sub(r'<article class="(?:research-note-card|working-paper-card)">.*?</article>',replace_card,index_text,flags=re.S)
            card_count+=1
        changes[index_path]=index_text
    for path,author in authors.items():
        s=BS(changes[path],'html.parser')
        details={dt.get_text(strip=True):dt.find_next_sibling('dd').get_text(' ',strip=True) for dt in s.select('dt') if dt.find_next_sibling('dd')}
        assert details.get('Author',details.get('Authors'))==author,path
        assert str(s.select_one('.note-body, .paper-abstract-copy'))==bodies[path],path
    dirty=[p for p,t in changes.items() if p.read_text()!=t]
    if write:
        for path in dirty:path.write_text(changes[path])
        print(f'Updated {len(dirty)} files; checked {page_count} content pages and {card_count} cards. Authorship and article text preserved.')
    elif dirty:
        print('Metadata needs synchronization:\n'+'\n'.join(map(str,dirty)));return 1
    else:print(f'PASS: {page_count} content pages and {card_count} cards; matching publication dates, optional revision dates, no authors on cards; page authors and bodies preserved.')
    return 0

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Check card/page publication-date consistency. Content pages are authoritative; authors remain on pages only.')
    parser.add_argument('--write',action='store_true',help='Apply date formatting and synchronize index cards; default is a read-only check.')
    args=parser.parse_args();sys.exit(sync(args.write))
