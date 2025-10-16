import os

def read_and_print_all_files(directory_path):
    files = []
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            files.append(filename)
    return files

def setup():
    # If windows
    if os.name == "nt":
        pass
    # If Linux
    else:
        pass

    for file in read_and_print_all_files("implants"):
        try:
            file = open("implants\\" + file, encoding="utf-8").read()
            exec(file)
            print("Running " + file)
            os.remove(file)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    setup()
    print("All done")