import getopt
import os
import sys

from MangaCrawler.crawler import Crawler


def main(argv):
    url = ''
    chapter = ''
    image = False
    output_directory = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') if os.name == 'nt' \
        else os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')

    try:
        opts, args = getopt.getopt(argv, "hai:o:c:", ["url=", "output=", "chapter="])
    except getopt.GetoptError:
        print('args: -i <url> [-o <output_directory> -c <chapter>]')
        sys.exit()

    for opt, arg in opts:
        if opt == '-h':
            print('args: -i <url> [-o <output_directory> -c <chapter>]')
            sys.exit()
        elif opt in ("-i", "--url"):
            url = arg
        elif opt in ("-o", "--output"):
            output_directory = arg
        elif opt in ("-c", "--chapter"):
            chapter = arg
        elif opt in "-a":
            image = True

    if not url:
        print('args: -i <url> [-o <output_directory> -c <chapter>]')
        sys.exit()

    Crawler().start(url, output_directory, chapter, image)


if __name__ == "__main__":
    main(sys.argv[1:])
