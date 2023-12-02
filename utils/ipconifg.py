import os

def executeIpConfig():
    os.system(f"ipconfig /all | findstr 물리적> ./ipconfig.txt")
    ret = ""
    with open("ipconfig.txt", 'r') as f:
        ret = f.readlines()
    ret = ret[0]
    ret = ret.split(":")[1][1:-1]
    return ret

if __name__ == "__main__":
    ret = executeIpConfig()
    print(ret)