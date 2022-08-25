# pingscan.py
Python, async, ping a ip range, or a list of IP/host
A simple tool for newbies.

* Before run
  * Make file executable
  ```chmod u+x pingscan.py```
  * Update first line with your own python path, or you run with 
  ```
  #python3 ./pingscan.py
  ```
  * Make alias in .zshrc(zsh) to make accessible from anywhere
  ```
  cp ./pingscan.py /usr/local/bin/
  alias pingscan=/usr/local/bin/pingscan.py
  ```

* ping a range of ip
```
#pingscan 192.168.10.1-254
started at 21:12:29, ping 192.168.10.1 - 254:
ip              time       loss    
192.168.10.1         4.060ms    0.0%    
192.168.10.18        1.281ms    0.0%    
192.168.10.6         195.356ms  0.0%    
192.168.10.2         -          100.0%
Completed in 6.13s
```

* ping a list of IP/host
```
#pingscan                
You could paste a list of IP/hostname below for ping scan, end input with two Enters:
114.114.114.114
202.96.134.133
114.114.115.115

started at 21:16:06, ping a list of IP/host:
ip/host              time       loss    
114.114.114.114      23.204ms   0.0%    
202.96.134.133       41.676ms   0.0%    
114.114.115.115      52.099ms   0.0%    
Completed in 4.07s
```

* Defaults, works in both Powershell and macOS
```
CONCURRENT_LIMIT = 100
PING_COUNT = 4
WAIT_MS = 1000  #1000ms
```
