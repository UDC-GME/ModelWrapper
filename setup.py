from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='ModelWrapper',
      version='0.1',
      description='Python module to manage scientific simulations',
      long_description=readme(),
      url='https://github.com/UDC-GME/ModelWrapper',
      author='Miguel Segade',
      author_email='miguelrsegade@gmail.com',
      classifiers=[
                'Development Status :: 2 - Pre-Alpha',
                'Intended Audience :: Science/Research',
                'Intended Audience :: Education',
                'Topic :: Scientific/Engineering',
                'Environment :: Console',
                'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
                'Programming Language :: Python :: 3.6',
      ],
      license='GPL',
      install_requires=[
            'numpy',
      ],
      include_package_data=True,
      zip_safe=False)

