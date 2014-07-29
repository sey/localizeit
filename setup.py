from distutils.core import setup

setup(
	name='localizeit',
	version='0.9.0',
	author='Florian Sey',
	author_email='florian.sey@gmail.com',
	url='https://github.com/sey/localizeit',
	description='Generate localization files for iOS and Android projects from Google Spreadsheets.',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python',
		'Topic :: Software Development :: Code Generators',
		'Topic :: Software Development :: Internationalization',
		'Topic :: Utilities'
	],
	requires=['oauth2client', 'httplib2', 'gspread', 'localizable']
)