import os

def executeNetstat(listenPort):
    os.system(f"netstat -a -n -p tcp | findstr {listenPort} > ./netstat.txt")
    ret = ""
    with open("./netstat.txt",'r') as f:
        ret = f.readlines()

    ret = ''.join(ret)
    ret1 = ret.split("\n")
    ret2 = ''
    for i in ret1:
        ret2 += '    '.join(i.split()[1:])
        ret2 += '\n'

    return ret2

if __name__ == "__main__":
    ret = executeNetstat(8080)
    print(ret)