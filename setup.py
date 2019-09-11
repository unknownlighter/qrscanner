from distutils.core import setup

setup(
    name='qrscanner',
    version='0.0.1',
    author='unknownlighter',
    author_email='unknownlighter@gmail.com',
    py_modules=['qrscanner'],
    description='QR Scanner',
    install_requires=[
        'zbar==0.10',
        'Pillow',
    ],
)
