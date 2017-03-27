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
    """
    Shell function which accepts a command and returns
    stdout, stderr, and command returncode
    """
    proc = Popen(x, shell=True, stdout=PIPE,  stderr=PIPE)
    out, err = proc.communicate()
    return out.strip(), err.strip(), proc.returncode


def inserter():
    """
    Function that stands ready in case Values not found on
    specific file, to insert it and continue
    """
    ins = ["make_resolv_conf(){", "    :", "}"]

    for cnk in ins:
        cmd = "echo " + "\"" + cnk + "\"" + " >>" + FILE
        rtn = bash(cmd)[2]
        if int(rtn) != 0:
            print "Can't insert to {} please verify manually".format(FILE)
            sys.exit(1)


def identifier(search):
    """
    This function will search for bash function named make_resolv_conf()
    and it will gather line range info of declaration / content
    """
    print "intr in func 3"
    com = "cat " + FILE  + " | grep -in" + " \"" + search +"\"" +" | cut -d':' -f1"
    print com
    pos = bash(com)[0]
    spos = pos
    print spos
    char = ""
    regex = re.compile("^(fi|#fi)")
    while not regex.match(char):
        comm = "cat " + FILE + " | sed -e \"" + str(spos) + "!" + "d" + "\""
        char = bash(comm)[0]
        spos = int(spos) + 1
    return pos, spos

def act_deact(*ar):
    try:
        numbs = identifier("is_on_read_only_partition /etc/resolv.")
        print "."
    except ValueError:
        print "Bash Function not defined in dhclient hooks ... Inserting the function and activating"
        inserter()
        numbs = identifier("is_on_read_only_partition /etc/resolv.")
    element = {}
    lst = []
    for line in range(int(numbs[0]), int(numbs[1])):
        command = "cat " + FILE + " | sed -e \"" + str(line) + "!" + "d" + "\""
        element[line] = bash(command)[0]
        tmp = bash(command)[0]
        lst.append({line, tmp})
    small = min(int(n) for n in element.keys())
    print element
    print lst
    if len(lst) != 3:
        print "If statment that controles function has more then 3 lines"
        sys.exit(1)
    if int(len(ar)) == 2:
    #Setting activation commands( s= shell, s= small, r= replace, o= others, c= command )
        ssc = "sed -i -e "  + "\'" + str(lst[0].keys()) + "s/#//' " + FILE
        src = "sed -i -e" + " \"" + str(lst[1].keys()) + "s" + "/.*/    return/" + "\"" +" "+ FILE
        soc = "sed -i -e" + " \"" + str(lst[2].keys()) + "s" + "/" + str(lst[2].values()) + "/" +\
                                                        str(lst[2].values())[1:] + "/" + "\"" +" "+ FILE
        act = "Activating..."
    elif int(len(ar)) == 1:
    #Setting DEactivation commands( s= shell, s= small, r= replace, o= others, c= command )
        ssc = "sed -i -e "  + "\'" + str(lst[0].keys()) + "s" + "/if \[/" + "#if \[/' " + FILE
        src = "sed -i -e" + " \"" + str(lst[1].keys()) + "s" + "/.*/    #Deactivated by CSRU/" + \
                                                                                "\"" + " " + FILE
        soc = cmd = "sed -i -e "  + "'" + str(lst[2].keys()) + "s" + "/" + str(lst[2].values()) + "/" + "#" + \
                                                                        str(lst[2].values()) + "/'"  +" " + FILE
        act = "Deactivating..."
    all = [small, ssc, src, soc, act, element]
    return all


def main():
    if args.A is True:
        holder = act_deact("-")
    elif args.D is True:
        holder = act_deact("-", "-")
    element = holder[5]
    print holder[4]
    for k, v  in element.items():
        if k == int(holder[0]):
            cmd = holder[1]
            #### COntinue FORM HERE (HOME)
            print "executin {}".format(cmd)
        elif "#Deactivated by CSRU" in v or "return" in v:
            cmd = holder[2]
            print "executin {}".format(cmd)
        else:
            cmd = holder[3]
            print "executin {}".format(cmd)
        ret = bash(cmd)[2]
        if ret != 0:
            print "Something went wrong when trying to edit {} on line".format(v)
            sys.exit(1)
    #else:
     #   print "Function already active"
      #  sys.exit(0)
if __name__ == "__main__":
    main()
