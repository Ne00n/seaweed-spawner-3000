class Templator:
    def genPeers(self,port,targets):
        peers,count = "",0
        for server,data in targets['servers'].items():
            if count > 0 and count != len(targets['servers']): peers += ","
            peers += data['vxlan']+":"+str(port)
            count = count +1
        return peers

    def genSystemd(self,type,ip,port,dirType,peerType,peerPort,targets):
        template = '''
        [Unit]
        Description=SeaweedFS '''+type+'''
        After=network.target

        [Service]
        Type=simple
        User=seaweedfs
        Group=seaweedfs

        ExecStart='''

        if type == "master":
            template += '/usr/local/bin/weed '+type+' -defaultReplication='+str(targets['replica'])+' -ip='+ip+' -ip.bind='+ip+' -port='+str(port)+' -'+dirType+'=/home/seaweedfs/'+type+' -'+peerType+'='+self.genPeers(peerPort,targets)
        elif type == "filer":
            template += '/usr/local/bin/weed '+type+' -ip='+ip+' -ip.bind='+ip+' -port='+str(port)+' -'+peerType+'='+self.genPeers(peerPort,targets)
        else:
            template += '/usr/local/bin/weed '+type+' -ip='+ip+' -ip.bind='+ip+' -port='+str(port)+' -'+dirType+'=/home/seaweedfs/'+type+' -'+peerType+'='+self.genPeers(peerPort,targets)

        template += '''
        WorkingDirectory=/home/seaweedfs/
        SyslogIdentifier=seaweedfs-'''+type+'''

        [Install]
        WantedBy=multi-user.target'''
        return template
