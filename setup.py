from setuptools import setup, find_packages


setup(
    name='scrapy-feedexporter-sftp',
    version='1.0.',
    url='https://github.com/scrapy-plugins/scrapy-feedexporter-sftp',
    description=(
        'Scrapy extension Feed Exporter Storage Backend to export items to an '
        'SFTP server'
    ),
    long_description=open('README.rst').read(),
    author='Scrapy developers',
    license='BSD',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Framework :: Scrapy',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Framework :: Scrapy',
    ],
    install_requires=['paramiko>=1.16.0'],
    requires=['scrapy (>=1.0.3)', 'paramiko (>=1.16.0)'],
)
