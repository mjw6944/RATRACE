import subprocess

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

disableEncryption()