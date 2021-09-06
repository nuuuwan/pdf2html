import os
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from utils import ds, filex, www

from pdf2html._utils import get_dir_url, log, parse_url


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
    for pdf_link in pdf_links:
        short_name = pdf_link.split('/')[-1]
        _li = ET.SubElement(_ul, 'li')
        ET.SubElement(_li, 'a', {'href': pdf_link}).text = short_name

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
