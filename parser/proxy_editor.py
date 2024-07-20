with open("parser/proxy.txt") as file:
    data = [line.replace("\n", "") for line in file.readlines()]

proxies = []
for url in data:
    _url = url.split("@")
    us_p = _url[1].split(":")
    username = us_p[0]
    password = us_p[1]
    ip = _url[0][7:]

    proxy = 'http://' + username + ':' + password + "@" + ip
    
    proxies.append(proxy)

for proxy in proxies:
    with open("parser/new_proxy.txt", "a") as file:
        file.write(proxy+"\n")