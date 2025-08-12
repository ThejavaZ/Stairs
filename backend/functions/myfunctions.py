import os

def clear():
    '''
    Clean the console.
    '''
    os.system("cls") if os.name == "nt" else os.system("clear")
    
def add_archive(directory:str):
    '''
    Search Archive
    '''
    BASE_DIR = os.getcwd()
    
    dir = f"{BASE_DIR}/{directory}"
    print(dir)