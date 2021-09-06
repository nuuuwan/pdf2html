import os
import shutil

from pdf2html._utils import CSS_FILE, DIR_ROOT

if __name__ == '__main__':
    shutil.rmtree(DIR_ROOT)
    os.mkdir(DIR_ROOT)
    shutil.copy2(
        CSS_FILE,
        os.path.join(
            DIR_ROOT,
            'styles.css',
        ),
    )
