#!/usr/bin/python
import sys
from subprocess import Popen, PIPE
import re
import argparse

PAR = argparse.ArgumentParser(description="This script will activate / deactivate the \
                                                                  make_resolve_conf bash function which is \
                                                                   used by the DHCP Client / usually used \
                                                                    in DHClient hooks")

PAR.add_argument("-A", dest="A", required=False, action='store_true', help="Having this switch enabled, it will Activate the function")
PAR.add_argument("-D", dest="D", required=False, action='store_true', help="Having this switch enabled, it will Deactivate the function")
PAR.add_argument("-f", dest="f", required=True, help="This switch is used to specify the DHClient hooks file location \
                                                                                 ex: in Fedora based distros is located in /etc/dhclient-enter-hooks")
args = PAR.parse_args()

FILE = args.f

def bash(x):
    proc = Popen(x, shell=True, stdout=PIPE,  stderr=PIPE)
    out, err = proc.communicate()
    return out.strip(), err.strip(), proc.returncode
def inserter():
    """
    Function that stands ready in case Values not found on
    specific file, to insert it and continue
    """
    ins = ["make_resolv_conf(){", "    :", "}"]

    for CHUNK in ins:
        CMD = "echo " + "\"" + CHUNK + "\"" + " >>" + FILE
        RTN = bash(CMD)[2]
        if int(RTN) != 0:
            print "Can't insert to {} please verify manually".format(FILE)
            sys.exit(1)
def identifier():
    """
    This function will search for bash function named make_resolv_conf()
    and it will gather line range info of declaration / content
    """
    COM = "cat " + FILE  + " | grep -in" + " \"" + "make_resolv_conf(){" +"\"" +" | cut -d':' -f1"
    POSITION = bash(COM)[0]
    STARTERPOS = POSITION
    CHARACTER = ""
    regex = re.compile("(\#{1}\}|\}{1})")
    while not regex.match(CHARACTER):
        comm = "cat " + FILE + " | sed -e \"" + str(STARTERPOS) + "!" + "d" + "\""
        CHARACTER = bash(comm)[0]
        STARTERPOS = int(STARTERPOS) + 1
    return POSITION, STARTERPOS

def main_deactivate():
    """
    This function will loop on the line numbers of the BASH function found,
    it will deactivate the function if found active
    """
    try:
        numbs = identifier()
    except ValueError:
        print "Bash Function not defined in dclient hooks... Inserting..."
        inserter()
        numbs = identifier()
    element = {}
    for line in range(int(numbs[0]), int(numbs[1])):
        command = "cat " + FILE + " | sed -e \"" + str(line) + "!" + "d" + "\""
        element[line] = bash(command)[0]
    if "#}" in element.values():
        print "Bash Function already commented out"
        sys.exit(0)
    elif ":" not in element.values() or "#Deactivated" not in element.values():
        print "Deactivating Function"
        for k, v  in element.items():
            if ":" in v:
                cmd = "sed -i -e" + " \"" + str(k) + "s" + "/.*/    #Deactivated by CSRU/" + \
                                                                                                         "\"" + " " + FILE
            else:
                cmd = "sed -i -e" + " \"" + str(k) + "s" + "/" + str(v) + "/" + "#" + \
                                                                         str(v) + "/" + "\"" +" " + FILE
            ret = bash(cmd)[2]
            if ret != 0:
                print "Something went wrong when trying to edit {} on line".format(v)
                sys.exit(1)
    elif ":" in element.values():
            print "Resolve.conf override function found as disabled "
            sys.exit(0)


def main_activate():
    try:
        numbs = identifier()
    except ValueError:
        print "Bash Function not defined in dhclient hooks ... Inserting the function and activating"
        inserter()
        numbs = identifier()
    element = {}
    for line in range(int(numbs[0]), int(numbs[1])):
        command = "cat " + FILE + " | sed -e \"" + str(line) + "!" + "d" + "\""
        element[line] = bash(command)[0]
    if "#Deactivated" in element.values() or ":" not in element.values():
        print "Activating Bash Function"
        for k, v  in element.items():
            if "#Deactivated" in v:
                cmd = "sed -i -e" + " \"" + str(k) + "s" + "/.*/    :/" + "\"" +" "+ FILE
            else:
                cmd = "sed -i -e" + " \"" + str(k) + "s" + "/" + str(v) + "/" +\
                                                         str(v)[1:] + "/" + "\"" +" "+ FILE
            ret = bash(cmd)[2]
            if ret != 0:
                print "Something went wrong when trying to edit {} on line".format(v)
                sys.exit(1)
    else:
        print "Function already active"
        sys.exit(0)





if __name__ == "__main__":
    if args.A is True:
        main_activate()
    elif args.D is True:
        main_deactivate()
    else:
        print "Please use --help, switches are required"