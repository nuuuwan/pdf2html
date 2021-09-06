import os

from urllib.parse import urlparse
from bs4 import BeautifulSoup
from utils import www, ds, filex, dt, hashx

from pdf2html._utils import log
DIR = '/tmp/pdf2html'
N_HASH = 8

def parse_url(url):
    url_parts = urlparse(url)
    root = url_parts.scheme + '://' + url_parts.netloc
    return dict(
        root=root,
        netloc=url_parts.netloc,
    )

def get_dir_url(url):
    url_parts = parse_url(url)
    netloc = url_parts['netloc']
    dir_only = dt.to_kebab(netloc) + '-' + hashx.md5(url)[:N_HASH]
    dir = os.path.join(DIR, dir_only)
    if not os.path.exists(DIR):
        os.mkdir(DIR)
    if not os.path.exists(dir):
        os.mkdir(dir)
    return dir


def get_pdf_links(url):
    log.info(f'Building contents for {url}')
    html = www.read(url)
    soup = BeautifulSoup(html, 'html.parser')

    url_parts = parse_url(url)
    root = url_parts['root']

    pdf_links = []
    for a_pdf_link in soup.find_all('a'):
        href = a_pdf_link.attrs.get('href')
        if '.pdf' == href[-4:]:
            if 'http' not in href:
                href = f'{root}{href}'
            pdf_links.append(href)
    pdf_links = sorted(ds.unique(pdf_links))
    n_pdf_links = len(pdf_links)
    log.info(f'Found {n_pdf_links} for {url}')
    return pdf_links

def build_contents(url):
    pdf_links = get_pdf_links(url)

    def render_pdf_link(pdf_link):
        short_name = pdf_link.split('/')[-1]
        return f'* [{short_name}]({pdf_link})'

    md_lines = [
        f'# [{url}]({url})',
    ] + list(map(
        render_pdf_link,
        pdf_links,
    ))
    dir_url = get_dir_url(url)
    md_file = os.path.join(dir_url, 'README.md')
    filex.write(md_file, '\n'.join(md_lines))
    log.info(f'Wrote contents for "{url}" to {md_file}')




if __name__ == '__main__':
    url = os.path.join(
        'https://www.epid.gov.lk',
        'web/index.php?',
        'option=com_content&view=article&id=233&lang=en',
    )
    build_contents(url)
