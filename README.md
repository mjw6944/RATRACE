# RATRACE
RATRACE is my fragile attempt at reviving and almagamating several pervious tools I have worked on both in academaia and work.

## RATRACE COMPONENTS
So far, it consists of the following parts:

**main.py** - The primary C2 server (RATRACE, as it were) to be run on the attacker's device. Supports a CLI GUI using pwnlib and can quick send commands via said interface. Essentially the entire c2 could be controlled with just an up, down, and enter input.

**implants** - the directory containing current and future implants | All implants follow a structure which makes them plug-n-play with RATRACE

**implants/implanttemplate.py** - The general outline of a RATRACE implant, not intended for actual use

**implants/copybarav2.py** - implant designed to cause mayhem, creates uncloseable blocking windows with various properties. Additionally, can be triggered to jam clipboard use. Supports boring commands too, I guess.

**implants/mimikity.py** - (WIP) Utilizes the "Store Passwords Using Reversible Encryption" on windows alongside alot of stolen impacket classes to fetch cleartext passwords from ntds.dit

**framework** - Files nessisary for mimikitty to function, ignore until MIMIKITTY is ready

**TODO.TXT** - Everything I want to do in the future, including UI improvements, personal touches, more implants, defender evasion tech, quality of life improvements, and *actually getting mimikitty to work*.
