import os

def executeIpConfig():
    os.system(f"ipconfig /all | findstr /i /c:어댑터 /c:물리적 /c:미디어> ./ipconfig.txt")
    ret = ""
    with open("ipconfig.txt", 'r') as f:
        ret = f.readlines()
    connect = True
    adap = ""
    addr = ""
    for i in ret:
        tmp = i.strip()
        if "어댑터" in tmp:
            adap = tmp[:-1]
            connect = True
        elif "미디어" in tmp:
            connect = False
        elif "물리적" in tmp:
            if connect:
                addr = tmp.split(" : ")[-1]
                break

    if connect:
        ret = f"{addr}({adap})"
    else:
        for i in ret:
            tmp = i.strip()
            if "어댑터" in tmp:
                adap = tmp[:-1]
            elif "물리적" in tmp:
                addr = tmp.split(" : ")[-1]
                break
        ret = f"{addr}({adap})"
    return ret

if __name__ == "__main__":
    ret = executeIpConfig()
    print(ret)