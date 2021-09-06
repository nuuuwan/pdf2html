import logging
import os
import xml.etree.ElementTree as ET

import camelot
from pdf2image import convert_from_path
from utils import filex, www

from pdf2html._utils import get_file, log, get_data_type

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
    _div_page = ET.SubElement(_body, 'div', {'class': 'div-page'})

    prev_page = None
    i_table1 = 0
    for i_table, table in enumerate(tables):
        report = table.parsing_report
        if report['whitespace'] > WHITESPACE_LIMIT:
            continue
        page = report['page']
        if prev_page != page:
            ET.SubElement(_body, 'h4').text = f'Page {page}'
            i_image1 = (int)(page)
            image_file = get_file(url, pdf_url, f'page-{i_image1:04d}.png')
            ET.SubElement(_body, 'img', {'src': image_file})
            prev_page = page
            i_table1 = 0
            _div_page = ET.SubElement(_body, 'div', {'class': 'div-page'})

        rows = table.df.values.tolist()
        i_table1 += 1

        _table = ET.SubElement(_div_page, 'table')
        ET.SubElement(_table, 'caption').text = f'Table {i_table1} - Page {page}'

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
                    class_ = 'td-' + get_data_type(cell)
                    ET.SubElement(_row, 'td', {'class': class_}).text = cell

    html = ET.tostring(_html).decode()
    complete_html_file = get_file(url, pdf_url, 'html')
    filex.write(complete_html_file, html)
    log.info(f'Wrote HTML to {complete_html_file}')

    download_images(url, pdf_url)


def download_images(url, pdf_url):
    pdf_file = get_file(url, pdf_url, 'pdf')
    log.info(f'Downloading images for {pdf_file}')
    images = convert_from_path(pdf_file)
    for i_image, image in enumerate(images):
        i_image1 = i_image + 1
        image_file = get_file(url, pdf_url, f'page-{i_image1:04d}.png')
        image.save(image_file, 'png')
        log.info(f'Downloaded images {image_file}')


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
