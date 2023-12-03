import socket

def gethostbyaddr(ip_address):
    message = ""
    try:
        host_name, _ = socket.getnameinfo((ip_address, 0), socket.NI_NAMEREQD)
        message = f"The host name for IP address {ip_address} is: {host_name}"
    except socket.error as e:
        message = f"Unable to get host name for {ip_address}. Error: {e}"
    return message

def gethostbyname(domain):
    message = ""
    try:
        ip_address = socket.gethostbyname(domain)
        message = f"The IP address of {domain} is: {ip_address}"
    except socket.error as e:
        message = f"Unable to get IP address for {domain}. Error: {e}"
    return message

if __name__ == "__main__":
    print(gethostbyname("google.com"))
    print(getnamebyhost("8.8.8.8"))