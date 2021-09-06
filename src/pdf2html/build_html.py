import logging
import os
import xml.etree.ElementTree as ET

import camelot
from utils import filex, www

from pdf2html._utils import get_file, log

PAGES = 'all'
WHITESPACE_LIMIT = 45
logging.getLogger('pdfminer').setLevel(logging.WARNING)


def download_pdf(url, pdf_url):
    pdf_file = get_file(url, pdf_url, 'pdf')

    if os.path.exists(pdf_file):
        log.warning(f'{pdf_file} already exists')
        return pdf_file

    www.download_binary(pdf_url, pdf_file)
    log.info(f'Downloaded "{pdf_url}" to {pdf_file}')
    return pdf_file


def build_html(url, pdf_url):
    log.info(f'Building HTML for "{pdf_url}"')
    pdf_file = download_pdf(url, pdf_url)
    tables = camelot.read_pdf(pdf_file, pages=PAGES)
    n_tables = len(tables)
    log.info(f'Extracted {n_tables} table(s) from {pdf_file}')

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
    short_name = pdf_url.split('/')[-1]
    ET.SubElement(_body, 'h1').text = short_name
    _p = ET.SubElement(_body, 'p')
    _p.text = 'Source: '
    ET.SubElement(_p, 'a', {'href': pdf_url}).text = pdf_url

    prev_page = None
    for i_table, table in enumerate(tables):
        report = table.parsing_report
        if report['whitespace'] > WHITESPACE_LIMIT:
            continue
        page = report['page']
        if prev_page != page:
            ET.SubElement(_body, 'h4').text = f'Page {page}'
            prev_page = page
        rows = table.df.values.tolist()

        _table = ET.SubElement(_body, 'table')
        for row in rows:
            max_act_rows = 1
            for cell in row:
                cell_parts = cell.split('\n')
                max_act_rows = max(
                    max_act_rows,
                    len(cell_parts),
                )
            act_rows = []
            for i in range(0, max_act_rows):
                act_row = []
                for cell in row:
                    cell_parts = cell.split('\n')
                    for i_cell_part, cell_part in enumerate(cell_parts):
                        if i_cell_part == i:
                            act_row.append(cell_part)

                act_rows.append(act_row)
            for act_row in act_rows:
                _row = ET.SubElement(_table, 'tr')
                for cell in act_row:
                    ET.SubElement(_row, 'td').text = cell

    html = ET.tostring(_html).decode()
    complete_html_file = get_file(url, pdf_url, 'html')
    filex.write(complete_html_file, html)
    log.info(f'Wrote HTML to {complete_html_file}')


if __name__ == '__main__':
    URL = os.path.join(
        'https://www.epid.gov.lk',
        'web/index.php?',
        'option=com_content&view=article&id=233&lang=en',
    )
    PDF_URL = os.path.join(
        'https://www.epid.gov.lk',
        'web/images/pdf/corona_virus_death_analysis',
        'death_analysis_from_21.08.2021_to_27.08.2021.pdf',
    )
    build_html(URL, PDF_URL)
