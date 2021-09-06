import logging
import os
import shutil

import camelot
from utils import filex, hashx, www

from pdf2html._utils import CSS_FILE, DIR_ROOT, get_dir_url, log

logging.getLogger('pdfminer').setLevel(logging.WARNING)


def get_file(url, pdf_url, prefix_ext):
    dir_url = get_dir_url(url)
    pdf_hash = hashx.md5(pdf_url)[:8]
    return os.path.join(dir_url, f'{pdf_hash}.{prefix_ext}')


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
    tables = camelot.read_pdf(pdf_file, pages='all')
    n_tables = len(tables)
    log.info(f'Extracted {n_tables} table(s) from {pdf_file}')

    short_name = pdf_url.split('/')[-1]
    inner_html = ''
    prev_page = None
    for i_table, table in enumerate(tables):
        report = table.parsing_report
        page = report['page']

        if prev_page != page:
            inner_html += f'<h4>Page {page}</h1>'
            prev_page = page

        inner_html += str(table.parsing_report)

        csv_file = get_file(url, pdf_url, f'{i_table}.csv')
        table.to_csv(csv_file)
        log.info(f'Saved table to {csv_file}')

        html_file = get_file(url, pdf_url, f'{i_table}.html')
        table.to_html(html_file)

        html_for_table = filex.read(html_file)
        inner_html += html_for_table

    complete_html = f'''
<html>
    <head>
        <link rel="stylesheet" href="../styles.css">
    </head>
    <body>
        <h1>{short_name}</h1>
        <p>
            Source:
            <a href="{pdf_url}">
                {pdf_url}
            </a>
        </p>
        {inner_html}
    </body>
</html>
    '''
    complete_html_file = get_file(url, pdf_url, 'complete.html')
    filex.write(complete_html_file, complete_html)
    log.info(f'Wrote HTML to {complete_html_file}')
    shutil.copy2(
        CSS_FILE,
        os.path.join(
            DIR_ROOT,
            'styles.css',
        ),
    )


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
