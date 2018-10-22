from setuptools import setup, find_packages

VERSION = "0.0"

setup(
    name='wikibase_universal_bot',
    version=VERSION,
    author='Diego Chialva',
    description='Python package for writing to any Wikibase instance without the need to code for specific bots.',
    license='MIT', #'AGPLv3'
    keywords='Wikibase data uploading universal-bot',
    url='https://github.com/dcodings/Wikibase_Universal_Bot',
    packages=find_packages(exclude=['.git*', '*logs', '*output']),
    include_package_data=False,
    # long_description=read('README.md'),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 0 - Beta",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: Wikibase users (also untechnical)",
        "Topic :: Utilities"
    ],
    install_requires=[
        'requests',
        'pandas',
        'datetime',
        'argparse',
        'wikidataintegrator==0.0.555', #0.0.509',
        'configparser',
        'pyyaml'
    ],
    package_data={
        # If any package contains LICENSE.txt files, include them:
        '': ['LICENSE.txt'],
        # And include also the following data files in subpackages:
        #'resources': ['example_connection_integrator_config_Orig.ini', 'orig_swiss_grants_model.yaml', 'origBasicItemsModel.yaml'],
    },
    data_files=[('.',['LICENSE.txt', 'README.md','ExampleBlock.png']),
                ('resources',['resources/example_connection_integrator_config_full.ini', 'resources/example_connection_integrator_config_prizes.ini', 'resources/prizes_model.yaml', 'resources/origBasicItemsModel.yaml', 'resources/prizes_model.yaml', 'resources/prizes.csv'])],
    exclude_package_data={
        '': ['*.csv', '*.pkl', '*.txt', '*.ini', '*.yaml', '*.pyOLD'],
        },
)
