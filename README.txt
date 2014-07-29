# localizeit

localizeit is a command line tool to generate localization files for iOS and Android projects from Google Spreadsheets.

## Install

    [sudo] easy_install --upgrade localizeit

or

    [sudo] python setup.py install

You will need to provide the localizeit.json configuration file with a client ID and client SECRET.  
You can create an new project at this url https://console.developers.google.com/project.  
Once created, click on your project name and go to APIS & AUTH => Credentials => Create new Client ID.  
Select "Installed application" for the APPLICATION TYPE and "Other" for the INSTALLED APPLICATION TYPE.

Create a file named localizeit.json with the following structure:
<pre><code>{  
	"client_id": "42.apps.googleusercontent.com",  
	"client_secret": "ABCDEFGH"  
}
</code></pre>

## Basic Usage

    python localizeit.py generate (android|ios) -s "Your i18n Google Spreadsheet" -o <output_dir>

## TODO

- Automatically detects language columns in the Google Spreadsheet