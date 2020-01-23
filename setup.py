from setuptools import setup

setup(
    name='acfun-uploader-cli',
    version='0.1.0',
    description='Acfun video uploader command line based on selenium.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
    ],
    keywords='acfun video uploader chrome selenium',
    url='https://github.com/xingheng/acfun-uploader-cli',
    author='Will Han',
    author_email='xingheng.hax@qq.com',
    license='unlicense',
    python_requires='>=3',
    packages=['acfun_uploader_cli'],
    install_requires=[
        'coloredlogs>=10.0',
        'configparser>=4.0.2',
        'selenium>=3.141.0',
    ],
    entry_points={
        'console_scripts': ['funniest-joke=funniest.command_line:main'],
    },
    include_package_data=True,
    zip_safe=False
)
