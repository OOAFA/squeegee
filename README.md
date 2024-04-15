# Squeegee

A collection of tools using OCR to extract potential usernames from RDP screenshots.

## Installing within a virtual environment ( no root needed )
```
$ python3 -m virtualenv venv
$ source venv/bin/activate
$ cd venv
$ git clone https://github.com/OOAFA/squeegee
$ cd squeegee
$ pip install -r requirements.txt
```

## Extract.py
This tool is used to copy screen captures out of Shodan search result logs stored as base64 image content.

## squeegee.py

This tool is used to extract useful strings from RDP screen captures and identify the OS running on the host, whether missing patches have been identifed, the domain (if any) the host is joined to, and usernames displayed on the logon screen. squeegee.py uses the easyocr library, this library is likely to be more accurate on a system with a supported GPU. Depending on the resolution of the target image, string detection may be inaccurate. Any unwanted strings should be added to the filter.txt file to suppress display in reporting output.


### Getting Started:

Example Command: `python3 squeegee.py -f /image/folder`

Example Command: `python3 squeegee.py -C --nohtml`

Example Command: `python3 squeegee.py -L --nohtml`

Example Command: `python3 squeegee.py -c 0.5 -f /image/folder`

Example Command: `python3 squeegee.py -l 'en' 'ru' -f /image/folder`

Example Command: `python3 extract.py -f shodan.json.gz -D /image/folder`

### Sample HTML Report Output:

The following image shows the table of contents. Report pages are created for each detected operating system version and a count of each type is included. At the bottom of the table of contents is a link to a list of unique useranames discovered in the group.

![Example RDP Entry](https://github.com/OOAFA/squeegee/blob/main/TableOfContents.png?raw=true)

The following image shows an individual entry in the HTML report. String content on the image is interpreted to identify the operating system, whether patches are missing, and the domain the system belongs to. Meaningless strings are filtered from the output and usernames are extracted, listed on the page, and included in a text-based users file.

![Example RDP Table of Contents](https://github.com/OOAFA/squeegee/blob/main/RDPEntry.png?raw=true)

### Filtering and Signatures:

RDP screen captures often contain information that is not useful in the context of username extraction and host characteristic identification. Filtered strings are included in files found in the filters directory of this project that are line terminated. The filter files are are prefixed with the targeted language code (example: English filter file = en.filter.txt).

Signatures are used to identify useful characteristics in a RDP screen capture like Active Directory domain, operating system version, and whether the host is missing updates. All signature files are found in the signatures directory of this project. Signatures to identify Active Directory domain and missing updates are line terminated. Signatures to identify operating systems are stored in JSON format to minimize duplication. All signature files are prefixed with the targeted language code (example: English variants = en.domain.txt, en.missingupdates.txt, en.os.json).

The easiest method to generate new filter and signature files is to run the tool with no support for the targeted language, then transcribe unnecessary strings into the appropriate file.

### Credits:
David Fletcher
github.com/aut0m8r
