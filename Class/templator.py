class Templator:
    def genPeers(self,port,targets):
        peers,count = "",0
        for server,data in targets['servers'].items():
            if count > 0 and count != len(targets['servers']): peers += ","
            peers += data['vpn']+":"+str(port)
            count = count +1
        return peers

    def genSystemd(self,type,ip,port,dirType,peerType,peerPort,targets,dc=False,rack=False):
        disableHttp = "-disableHttp" if targets['disableHttp'] else ""
        user = "root" if type == "mount" else "seaweedfs"
        template = f'''[Unit]
Description=SeaweedFS {type}
After=network.target
StartLimitBurst=3
StartLimitIntervalSec=200

[Service]
Type=simple
User={user}
Group=seaweedfs
Restart=on-failure
RestartSec=60s

ExecStartPre=/bin/sh -c 'until ping -c1 '''+ip+'''; do sleep 1; done;'
ExecStart='''

        if type == "master":
            template += f'/usr/local/bin/weed master {disableHttp} -defaultReplication={targets["replica"]} -ip={ip} -ip.bind={ip} -port={port} -{dirType}=/home/seaweedfs/{type} -{peerType}={self.genPeers(peerPort,targets)}'
        elif type == "filer":
            template += f'/usr/local/bin/weed filer {disableHttp} -localSocket=/home/seaweedfs/filer.sock -ip={ip} -ip.bind={ip} -port={port} -{peerType}={self.genPeers(peerPort,targets)}'
        elif type == "mount":
            template += f'''/usr/local/bin/weed mount -filer={self.genPeers(port,targets)} -dir={dc} -filer.path={rack}
ExecStop=/usr/bin/umount -l {dc}'''
        else:
            template += '/usr/local/bin/weed '+type+' -ip='+ip+' -ip.bind='+ip+' -port='+str(port)+' -'+dirType+'=/home/seaweedfs/'+type+' -dataCenter='+dc+' -rack='+rack+' -'+peerType+'='+self.genPeers(peerPort,targets)

        template += f'''
WorkingDirectory=/home/seaweedfs/
SyslogIdentifier=seaweedfs-{type}

[Install]
WantedBy=multi-user.target'''
        return template
