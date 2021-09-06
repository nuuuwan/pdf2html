"""Utils."""
import logging
import os
from urllib.parse import urlparse

from utils import dt, hashx

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('pdf2html')


DIR_ROOT = '/tmp/pdf2html'
N_HASH = 8
CSS_FILE = 'src/pdf2html/styles.css'


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
    dir = os.path.join(DIR_ROOT, dir_only)
    if not os.path.exists(DIR_ROOT):
        os.mkdir(DIR_ROOT)
    if not os.path.exists(dir):
        os.mkdir(dir)
    return dir


def get_file(url, pdf_url, prefix_ext):
    dir_url = get_dir_url(url)
    pdf_hash = hashx.md5(pdf_url)[:8]
    return os.path.join(dir_url, f'{pdf_hash}.{prefix_ext}')

def get_data_type(x):
    try:
        int_x = (int)(x)
        return 'int'
    except ValueError:
        try:
            float_x = (float)(x)
            return 'float'
        except ValueError:
            if '%' in x:
                return 'percent'
    return 'unknown'
