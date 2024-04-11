#!/usr/bin/env python3

import os
import sys
import json
import argparse
import time
import easyocr

from modules import objects

def create_cli_parser():
    parser = argparse.ArgumentParser(
            add_help=False, description="Squeegee is a tool used to scrape text from RDP screen\
            captures contained in a single folder.")
    parser.add_argument('-h', '-?', '--h', '-help', '--help', action="store_true", help=argparse.SUPPRESS)

    input_options = parser.add_argument_group('Input Options')
    input_options.add_argument('-l', help='List of two-character ISO 639 language codes to process.\
            Current dictionaries support en and ru languages. Supported languages is dependent on support\
            by the easyocr parser. Defaults to [\'en\',\'ru\'].',metavar='\'en\' \'ru\'',default=['en','ru'], nargs='+')
    input_options.add_argument('-f', help='Input folder containing RDP screen captures in JPG format.\
            Output log and HTML report will be written to this folder.',metavar='/tmp/rdp/images')
    input_options.add_argument('-c', type=float, help='Baseline confidence interval for text\
            detection. Value must be between 0 and 1. Lower value indicates lower confidece for correct\
            string match. Strings with a confidence interval below this value will be suppressed. Defaults to 0.6',metavar='0.6',default=0.6)

    filter_options = parser.add_argument_group('Filtering and Signature Matching')
    filter_options.add_argument('--nofilter', help='Disable string filtering. Can be useful for troubleshooting\
            ',default=False, action='store_true')
    filter_options.add_argument('--nosig', help='Disable signature matching.',default=False, action='store_true')
    
    output_options = parser.add_argument_group('Output Options')
    output_options.add_argument('-H','--nohtml', help='Disable HTML report output (Default on). Will be written to input folder as RDPScrape.html.', default=False, action='store_true')
    output_options.add_argument('-C','--console', help='Enable Console output.',default=False, action='store_true')
    output_options.add_argument('-L','--log', help='Enable Log File output. Will be written to input folder as RDPScrape.log',default=False, action='store_true')

    args = parser.parse_args()
    args.date = time.strftime('%Y/%m/%d')
    args.time = time.strftime('%H:%M:%S')

    if args.h:
        parser.print_help()
        sys.exit()

    if args.f is None:
        print("[*] Error: You didn't specify a folder! I need a folder containing RDP screen captures!")
        parser.print_help()
        sys.exit()

    if ((args.f is not None) and not os.path.isdir(args.f)):
        print("[*] Error: You didn't specify the correct path to a folder. Try again!\n")
        parser.print_help()
        sys.exit()

    if (args.nohtml == True) and (args.console == False) and (args.log == False):
        print("[*] Error: You didn't specify an output type. At least one should be enabled.")
        parser.print_help()
        sys.exit()

    return args

def generate_html_report(screens, pages, outfolder):

    files_dict = {}
    os_count = {}

    for page in pages:
        targetFile = outfolder + '/' + page + ".html"
        if os.path.exists(targetFile):
            os.remove(targetFile)
        file = open(targetFile,'x')
        file.write(get_html_header(page))
        files_dict[page] = file
        os_count[page] = 0

    for screen in screens:
        files_dict[screen.operatingSystem].write(get_html_row(screen,outfolder))
        os_count[screen.operatingSystem] = os_count[screen.operatingSystem] + 1

    tocFile = outfolder + "/Report.html"
    if os.path.isfile(tocFile):
        os.remove(tocFile)

    toc = open(tocFile,'x')
    toc.write(get_toc_header())
    total = 0
    for operatingSystem in os_count:
        toc.write(get_toc_row(operatingSystem, os_count[operatingSystem], outfolder))
        total = total + os_count[operatingSystem]
    toc.write(get_total_row(total))
    toc.write(get_toc_footer())

    for file in files_dict:
        files_dict[file].write(get_html_footer())
        files_dict[file].close()

    print("[+] Processing complete. Output recorded in " + toc.name + ".")
    toc.close()

def get_html_header(title):
    page_content = """
    <html>
    <head>
        <title>Squeegee Report - {}</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" type="text/css"/>    </head>
    <body>
    <h2>Squeegee Report - {}</h2>
    <table border="1">
    <tr>
    <th>Capture Text</th>
    <th>RDP Screen Capture</th>
    </tr>
    """.format(title,title)
    return page_content

def get_html_footer():
    page_content = """
    </table>
    </body>
    </html>
    """
    return page_content

def get_html_row(screen, outfolder):
    if screen.isPatched == True:
        patched = "<br />"
    else:
        patched = "<br /><span style='color:red; font-weight: bold'>Missing Patches</span><br />"

    if len(screen.usernames) > 0:
        userFile = screen.fileName + ".txt"
        userLink = "<br /><b>Users File:</b><a href='" + userFile + "'>" + userFile + "</a>"
    else:
        userLink = ""

    page_content = """
    <tr>
        <td>
        <b>Filename:</b> {} {}
        <b>Domain:</b> {}<br/>
        <b>Usernames:</b><br/>
        &nbsp;&nbsp;&nbsp;&nbsp;{}
        {}
        </td>
        <td>
        <img src="{}" />
    </tr>
    """.format(screen.fileName,patched,screen.domain,'<br/>&nbsp;&nbsp;&nbsp;&nbsp;'.join(screen.usernames),userLink,screen.fileName)
    return page_content

def get_toc_header():
    page_content = """
    <html>
    <head>
        <title>Squeegee Report - Table of Contents</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" type="text/css"/>    </head>
    <body>
    <h2>Squeegee Report - Table of Contents</h2>
    <center>Report Generated on {} at {}
    <h2>Table of Contents</h2>
    <table border=1 style="width: 80%; margin-left: 10px; margin-right: 10px;">
    """.format(time.strftime('%Y/%m/%d'),time.strftime('%H:%M:%S'))
    return page_content

def get_toc_footer():
    page_content = """
    </table>
    <a href="allusers.txt">All Discovered Usernames</a>
    </center>
    </body>
    </html>
    """
    return page_content

def get_toc_row(operatingSystem, count, outfolder):
    page_content = """
    <tr>
    <td><a href="{}/{}.html">{}</a></td>
    <td align="center">{}</td>
    </tr>
    """.format(outfolder,operatingSystem,operatingSystem,count)
    return page_content

def get_total_row(count):
    page_content = """
    <tr>
    <td align="right"><b>Total</b></td>
    <td align="center">{}</td>
    </tr>
    """.format(count)
    return page_content

def get_banner():
    banner_content = """
  ---------------------------------------------------------------------------------
  | [ ].  Remote Desktop Connection (Squeegee)                   --    [ ]    X   |
  ---------------------------------------------------------------------------------
  |   .---------.   ___               _         ___         _   _                 |
  |   ||```````||  | _ \___ _ __  ___| |_ ___  |   \ ___ __| |_| |_ ___ _ __      |
  |   || \  \  ||  |   / -_) '  \/ _ \  _/ -_) | |) / -_|_-< / /  _/ _ \ '_ \     |
  |   ||  \  \ ||  |_|_\___|_|_|_\___/\__\___|_|___/\___/__/_\_\\\\__\___/ .__/     |
  |   ||.......||   / __|___ _ _  _ _  ___ __| |_(_)___ _ _            |_|        |
  |      )---(     | (__/ _ \ ' \| ' \/ -_) _|  _| / _ \ ' \                      |
  |  /_______(><)\  \___\___/_||_|_||_\___\__|\__|_\___/_||_|                     |
  |                                                                               |
  ---------------------------------------------------------------------------------
  |                                                                               |
  |   Computer:     [ Example: computer.blackhillsinfosec.com          ^]         |
  |                                                                               |
  |   User name:    David.Fletcher                                                |
  |                                                                               |
  |   The computer name field is blank. Enter a full remote computer              |
  |   name.                                                                       |
  |                                                                               |
  |   (^) Show Options                                    [ Connect ] [ Help]     |
  |                                                                               |
  ---------------------------------------------------------------------------------                       """
    return banner_content

def main():
    print(get_banner())
    cli_parsed = create_cli_parser()

    if cli_parsed.f.endswith('/'):
        folder = cli_parsed.f[:-1]
    else:
        folder = cli_parsed.f
    language_list = cli_parsed.l

    reader = easyocr.Reader(language_list)

    filtered = []
    missingupdates = []
    domainsig = []
    os_dict = {}

    if cli_parsed.nofilter == False:
        for language in language_list:
            filterFile = "./filters/" + language + ".filter.txt"
            if os.path.exists(filterFile):
                with open(filterFile) as filter_list:
                    filtered.extend(filter_list.read().splitlines())
            else:
                print("[!] No filter file exists for language: " + language)

    if cli_parsed.nosig == False:
        for language in language_list:
            updateFile = "./signatures/" + language + ".missingupdates.txt"
            if os.path.exists(updateFile):
                with open(updateFile) as missingupdates_list:
                    missingupdates.extend(missingupdates_list.read().splitlines())
            else:
                print("[!] No missing updates signature file exists for language: " + language)

            domainFile = "./signatures/" + language + ".domain.txt"
            if os.path.exists(domainFile):
                with open(domainFile) as domain_list:
                    domainsig.extend(domain_list.read().splitlines())
            else:
                print("[!] No domain signature file exists for language: " + language)

            osFile = "./signatures/" + language + ".os.json"
            if os.path.exists(osFile):
                with open("./signatures/" + language + ".os.json") as os_dictionary:
                    data = os_dictionary.read()
                    new_os = json.loads(data)
                    os_dict.update(new_os)
            else:
                print("[!] No OS signature file exists for language: " + language)

    if os.path.exists(folder):
        if cli_parsed.log == True:
            logfile = folder + '/Squeegee.log'
            if os.path.exists(logfile):
                os.remove(logfile)
            log_file = open(folder + '/Squeegee.log','x')
        files = os.listdir(folder)
        index = 0
        screens = []
        pages = []
        allusers = []

        print("[+] Processing files in " + folder + " please wait...")

        while index < len(files):
            filename = files[index]
            if filename.endswith('.jpg') or filename.endswith('.jpeg'):
               result = reader.readtext(os.path.join(folder,filename))
               screen = objects.RDPObject()
               screen.fileName = filename
               usernames = []
               for x in range(len(result)):
                   if result[x][2] > cli_parsed.c:
                       domain_match = result[x][1].split(":")
                       if (domain_match[0] in domainsig):
                           screen.domain = domain_match[1]
                       else:
                           if (result[x][1] in filtered):
                               if (result[x][1] in missingupdates):
                                   screen.isPatched = False
                               if (result[x][1] in os_dict):
                                   screen.operatingSystem = os_dict[result[x][1]]
                           else:
                               if (result[x][1] in missingupdates):
                                   screen.isPatched = False
                               if (result[x][1] in os_dict):
                                   screen.operatingSystem = os_dict[result[x][1]]
                               usernames.append(result[x][1])
                               if (result[x][1] not in allusers):
                                   allusers.append(result[x][1])

               screen.usernames = usernames

               if len(usernames) > 0:
                   screenUsersFile = os.path.join(folder,filename + ".txt")
                   if os.path.exists(screenUsersFile):
                       os.remove(screenUsersFile)

                   with open(screenUsersFile, mode='x') as userlog:
                       userlog.write('\n'.join(usernames))

               if cli_parsed.nohtml == False:
                    if screen.operatingSystem not in pages:
                       pages.append(screen.operatingSystem)

               screens.append(screen)

               if cli_parsed.console == True:
                   print("[+] - Filename: " + screen.fileName)
                   print("    [-] OS: " + screen.operatingSystem)
                   if (screen.isPatched == False):
                       print("    [!] Missing Updates") 
                   print("    [-] Domain: " + screen.domain)
                   print("    [-] Usernames: ")
                   for x in range(len(screen.usernames)):
                       print("          " + screen.usernames[x])
               if cli_parsed.log == True:
                   log_file.write("[+] - Filename: " + screen.fileName + "\n")
                   log_file.write("    [-] OS: " + screen.operatingSystem + "\n")
                   if (screen.isPatched == False):
                       log_file.write("    [!] Missing Updates\n") 
                   log_file.write("    [-] Domain: " + screen.domain + "\n")
                   log_file.write("    [-] Usernames: " + "\n")
                   for x in range(len(screen.usernames)):
                       log_file.write("          " + screen.usernames[x] + "\n")
    
            index += 1
        if cli_parsed.log == True:
            print("[+] Processing complete. Output recorded in " + log_file.name + ".")
            log_file.close()
        if cli_parsed.nohtml == False:
            generate_html_report(screens, pages, folder)

        if len(allusers) > 0:
            allUsersFile = os.path.join(folder,"allusers.txt")
            if os.path.exists(allUsersFile):
                os.remove(allUsersFile)

            with open(allUsersFile, mode='x') as alluserlog:
                allusers.sort()
                alluserlog.write('\n'.join(allusers))

    else:
        print("Screen capture folder does not exist")

if __name__ == "__main__":
    main()
