#!python
# vim: set fileencoding=utf-8 shiftwidth=4 tabstop=4 expandtab smartindent :

"""
Main program for analyzing the downloaded files.
Python 3 is highly recommended since it handles
unicode better.
"""

# Note to self: Keep this script working with
# both "python" (2.7.x) and "python3"!

__author__ = "Henrik Laban Torstensson, Andreas Söderlund, Timmy Larsson"
__license__ = "MIT"

import argparse
import os
import sys
import zipfile

if sys.version_info >= (3,):
    from io import StringIO
else:
    from cStringIO import StringIO

class ConsultationZipHandler:
    """
    Class analyzing zip files with consultation form responses
    """

    def __init__(self):
        self.categoryDict = {}
        self.count = 0
        self.extensionDict = {}
        self.fileList = []
        self.zipFiles = {} # filename -> ZipFile object

    def addZip(self, zipFilename):
        """Read statistics in zip file
        """

        zipFile = zipfile.ZipFile(zipFilename)
        self.zipFiles[zipFilename] = zipFile # Save in class dict

        # Loop through all files in the zip file
        # and count the number of files in different
        # categories and with different extensions
        for filename in zipFile.namelist():
            category = os.path.dirname(filename)
            formName = os.path.basename(filename)
            if formName == "":
                # Directory entry
                continue
            self.fileList.append(formName)
            self.count += 1
            if category in self.categoryDict.keys():
                self.categoryDict[category]["count"] += 1
            else:
                self.categoryDict[category] = {"count": 1}
            extension = formName.split(".")[-1]
            if extension in self.extensionDict.keys():
                self.extensionDict[extension]["count"] += 1
            else:
                self.extensionDict[extension] = {"count": 1}

    def listFiles(self):
        return self.fileList

    def getCount(self):
        return self.count

    def getCategories(self):
        return sorted(self.categoryDict.keys())

    def getCountInCategory(self, category):
        return self.categoryDict[category]["count"]

    def getExtensions(self):
        return sorted(self.extensionDict.keys())

    def getCountInExtension(self, extension):
        return self.extensionDict[extension]["count"]
        

def main():
    """Main function for running the analyzer.
    Options will be parsed from the command line."""

    availableCommands = ["analyze", "list-forms", "stats"]

    parser = argparse.ArgumentParser(description=__doc__)
    commandsHelp = "Available commands: %s" % (", ".join(availableCommands))
    parser.add_argument(metavar="CMD",
                        dest="command",
                        help=commandsHelp)
    parser.add_argument(metavar="ZIPFILE",
                        dest="files",
                        nargs="+",
                        help="Space separated list of zip files to handle")

    args = parser.parse_args()

    if not args.command in availableCommands:
        parser.error("Unknown command: %s" % (args.command))
    print("The following zip files will be handled:")
    print("\n".join(map(lambda s: "* %s" % (s), args.files)))

    print("")
    count = 0
    zip = ConsultationZipHandler()
    for zipFile in args.files:
        print("Handling %s..." % (zipFile))
        zip.addZip(zipFile)

    print("")
    if args.command == "list-forms":
        print("List of consultation forms:")
        for file in zip.listFiles():
            try:
                print("* %s" % (file))
            except UnicodeEncodeError:
                print("ERROR: Encoding error")
    elif args.command == "stats":
        print("Categories:")
        categories = zip.getCategories()
        for category in categories:
            print("  %-55s: %5d" % (category, zip.getCountInCategory(category)))
        print()
        print("File extensions:")
        for extension in zip.getExtensions():
            print("  %-6s: %5d" % (extension, zip.getCountInExtension(extension)))
        print("")
        print("NUMBER OF FILES: %d" % (zip.getCount()))
        print("")
        count += zip.getCount()
    elif args.command == "analyze":
        pass

if __name__ == "__main__":
    main()
