import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='orchestra',
    version='0.0.14',
    author='Christoph Berger',
    author_email='c.berger@tum.de',
    description='Bulk segmentation for the BraTS challenge',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/christophantonberger/orchestra',
    packages=['orchestra'],
    zip_safe=False,
    install_requires=[
          'SimpleITK',
          'numpy'
    ],
    entry_points={
        'console_scripts': [
            'brats-segment = orchestra.cli:segmentation',
            'brats-fuse = orchestra.cli:fusion',
            'brats-orchestra = orchestra.cli:segmentation'
        ],
      },
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
