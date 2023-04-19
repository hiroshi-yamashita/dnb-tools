import setuptools
import os


def requirements_from_file(file_name):
    return open(file_name).read().splitlines()


setuptools.setup(
    name="dnb_tool",
    version="0.1",
    author="Hiroshi Yamashita, Yuji Okamoto, Makito Oku",
    author_email="h.yamashita@ist.osaka-u.ac.jp, yuji.0001@gmail.com, oku@inm.u-toyama.ac.jp",
    description="DNB library",
    long_description="DNB library",
    install_requires=requirements_from_file('requirements.txt'),
    long_description_content_type="text/markdown",
    url="https://github.com/hiroshi-yamashita/dnb-tools",
    packages=setuptools.find_packages(),
    package_data={'dnb_tool': ['datasets/data/*']},
    entry_points={
        "console_scripts": [
            "dnb_example_tabular=dnb_tool.example_tabular:main",
            "dnb_example_timeseries=dnb_tool.example_timeseries:main",
            "dnb_tabular=dnb_tool.tabular_main:main",
            "dnb_timeseries=dnb_tool.timeseries_main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: Apache License 2.0",
        "Operating System :: OS Independent",
    ],
)
