# a traditional server

start server here by doing

```
/opt/workshop/socket-activation/server
```


then query the server 

```
curl localhost:8000
```

you will get a html, and see a log

```commandline
127.0.0.1 - - [07/Mar/2024 05:39:12] "GET / HTTP/1.1" 200 -
```

if you check lsof, you can see that the server is listening to port 8000

```commandline
[root@eth50-1 fwll]# lsof  -P  -p 5696 | grep LISTEN
python3 5696 root    3u  IPv4  20663      0t0   TCP *:8000 (LISTEN)

```
now shut it off and start 

---
[back to TOC](https://github.com/systemdemo/workshop/blob/main/workshop/README.md)