# aliyun_client.py 
## function
1. stop the vms
2. start the vms
3. reset the vms by the snapshot's name( include <<filter>>)  
```
python aliyun_client.py --stop
python aliyun_client.py --start
python aliyun_client.py --reset
```

### setting config.yml
```
mv config.yml.sample config.yml  
key_id: <<aliyun_key_id>>  
key_secret: <<aliyun_key_secret>>
region_id: cn-hangzhou
hosts:
- dev-10
- dev-7
- dev-8
- dev-9
filter: centos-7
wait_time: 5
```
### docker running
``` script
make build
make run
make run_stop 
make run_start
make run_reset
```

