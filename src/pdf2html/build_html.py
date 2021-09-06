import os
from pdf2html._utils import log

def build_html(pdf_url):
    log.info(f'Building HTML for "{pdf_url}"')


if __name__ == '__main__':
    URL = os.path.join(
        'https://www.epid.gov.lk',
        'web/images/pdf/corona_virus_death_analysis',
        'death_analysis_from_21.08.2021_to_27.08.2021.pdf',
    )
    build_html(URL)
