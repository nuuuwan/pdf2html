import os
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from utils import ds, filex, www

from pdf2html._utils import get_dir_url, get_file, log, parse_url


def get_pdf_urls(url):
    log.info(f'Building contents for {url}')
    html = www.read(url)
    soup = BeautifulSoup(html, 'html.parser')

    url_parts = parse_url(url)
    root = url_parts['root']

    pdf_urls = []
    for a_pdf_url in soup.find_all('a'):
        href = a_pdf_url.attrs.get('href')
        if '.pdf' == href[-4:]:
            if 'http' not in href:
                href = f'{root}{href}'
            pdf_urls.append(href)
    pdf_urls = sorted(ds.unique(pdf_urls))
    n_pdf_urls = len(pdf_urls)
    log.info(f'Found {n_pdf_urls} for {url}')
    return pdf_urls


def build_contents(url):
    pdf_urls = get_pdf_urls(url)

    _html = ET.Element('html')
    _head = ET.SubElement(_html, 'head')
    ET.SubElement(
        _head,
        'link',
        {
            'rel': 'stylesheet',
            'href': '../styles.css',
        },
    )
    _body = ET.SubElement(_html, 'body')
    ET.SubElement(_body, 'h1').text = url
    _ul = ET.SubElement(_body, 'ul')
    for pdf_url in pdf_urls:
        html_file = get_file(url, pdf_url, 'html')
        html_file_only = html_file.split('/')[-1]
        _li = ET.SubElement(_ul, 'li')
        class_ = 'a-pdf-url-missing'
        ET.SubElement(
            _li, 'a', {'href': pdf_url, 'class': class_, 'target': '_blank'}
        ).text = pdf_url

        if os.path.exists(html_file):
            class_ = 'a-pdf-url-exists'
            ET.SubElement(
                _li,
                'a',
                {'href': html_file_only, 'class': class_, 'target': '_blank'},
            ).text = ' (📃 tables as HTML)'

    html = ET.tostring(_html).decode()
    dir_url = get_dir_url(url)
    html_file = os.path.join(dir_url, 'index.html')
    filex.write(html_file, html)
    log.info(f'Wrote contents for "{url}" to {html_file}')


if __name__ == '__main__':
    URL = os.path.join(
        'https://www.epid.gov.lk',
        'web/index.php?',
        'option=com_content&view=article&id=233&lang=en',
    )
    build_contents(URL)
