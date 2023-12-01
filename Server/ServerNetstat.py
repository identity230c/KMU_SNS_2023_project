import os

def executeNetstat(listenPort):
    os.system(f"netstat -a -n -p tcp | findstr {listenPort} > ./netstat.txt")
    ret = ""
    with open("./netstat.txt",'r') as f:
        ret = f.readlines()
    return ''.join(ret)

if __name__ == "__main__":
    print(executeNetstat(8080))