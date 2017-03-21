#!/usr/bin/python
import sys
from subprocess import Popen, PIPE


def bash(x):
    proc = Popen(x, shell=True, stdout=PIPE,  stderr=PIPE)
    out, err = proc.communicate()
    return out.strip(), err.strip(), proc.returncode

def identifier():
    """
    This function will search for bash function named make_resolv_conf() 
    and it will gather line range info of declaration / content
    """

    POSITION = bash('cat test.txt | grep -in "make_resolv_conf(){" | cut -d":" -f1')[0]
    STARTERPOS = POSITION
    POWERPOS = POSITION
    char = ""

    while char != "}":
            comm = "cat test.txt | sed -e \"" + str(STARTERPOS) + "!" + "d" + "\""
            char = bash(comm)[0][0]
            STARTERPOS = int(STARTERPOS) + 1
    return POSITION, STARTERPOS

def main_deactivate():
    numbs = identifier()
    element = []
    for line in range(int(numbs[0]), int(numbs[1])):
        command = "cat test.txt | sed -e \"" + str(line) + "!" + "d" + "\""
        element.append(bash(command)[0])
    if ":" not in element:
        print "Deactivating Function"
        for i in element:
            #for num in range(int(numbs[0]), int(numbs[1])):
            cmd = "sed -i -e" + " \"" +  "s" + "/" + str(i) + "/" + "#" + str(i) + "/" + "\"" +" test.txt"
            ret = bash(cmd)[2]
            if ret != 0:
                print "Something went wrong when trying to edit {} on line".format(i)
    elif ":" in element:
            print "Resolve.conf override function found as disabled "
            



main_deactivate()