#!/usr/bin/env python3

import base64
import shodan
import shodan.helpers as helpers

import os
import sys
import argparse

def create_cli_parser():
    parser = argparse.ArgumentParser(
            add_help=False, description="Extract is a tool used to extract screen captures from Shodan\
            log output (.json.gz file).")
    parser.add_argument('-h', '-?', '--h', '-help', '--help', action="store_true", help=argparse.SUPPRESS)
    
    input_options = parser.add_argument_group('Input Options')
    input_options.add_argument('-f', help='Shodan log (.json.gz) input file containing RDP screen captures. Search\
            criteria should be scoped to appropriate networks and services to ensure that only RDP screen captures\
            are included in the results.', metavar='shodan_log.json.gz')

    output_options = parser.add_argument_group('Output Options')
    output_options.add_argument('-D', help='Output directory where extracted images should be saved.', metavar='/temp/shodan_images/')

    args = parser.parse_args()

    if args.h:
        parser.print_help()
        sys.exit()

    if args.f is None:
        print("[*] Error: You didn't specify an input file! I need a Shodan log to parse!")
        parser.print_help()
        sys.exit()

    if args.D is None:
        print("[*] Error: You didn't specify an output folder to save screen captures!")
        parser.print_help()
        sys.exit()

    return args


def main():

    args = create_cli_parser()
    
    shodan_log = args.f
    output_dir = args.D

    if not os.path.exists(output_dir):
	    os.mkdir(output_dir)

    screen_count = 0

    print("[-] Processing screen captures in {}...".format(shodan_log))


    for banner in helpers.iterate_files(shodan_log):
    	screenshot_instance = helpers.get_screenshot(banner)
	
    	if screenshot_instance is not None:
            screenshot_image = open('{}/{}.jpg'.format(output_dir, banner['ip_str']), 'wb')
            screenshot_image.write(base64.b64decode(screenshot_instance['data']))
            screen_count = screen_count+1
    print("[-] Successfully extracted {} screen captures from {} into {}.".format(screen_count,shodan_log,output_dir))

if __name__ == "__main__":
    main()
