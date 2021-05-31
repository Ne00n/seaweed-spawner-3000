import subprocess, time, json, re
from Class.templator import Templator

class SeaweedFS:

    targets = []

    def __init__(self,config="hosts.json"):
        print("Loading",config)
        with open(config) as handle:
            self.targets = json.loads(handle.read())

    def cmd(self,server,command,interactive):
        cmd = ['ssh','root@'+server,command]
        if interactive == True:
            return subprocess.check_output(cmd).decode("utf-8")
        else:
            subprocess.run(cmd)

    def prepare(self,server,data,delete=False,terminate=False):
        print("---",server,"Preparing","---")
        #Fetch old configs
        files = self.cmd(data['ip'],'ls /etc/systemd/system/',True)
        #Parse configs
        parsed = re.findall("^SeaweedFS[A-Za-z0-9.]+",files, re.MULTILINE)
        #Disable old configs
        for service in parsed:
            print("Stopping "+service)
            self.cmd(data['ip'],'systemctl stop '+service+' && systemctl disable '+service,False)
            if delete: self.cmd(data['ip'],'rm /etc/systemd/system/'+service,False)
        if terminate: self.cmd(data['ip'],'userdel -r seaweedfs',False)


    def clean(self):
        for server,data in self.targets['servers'].items():
            self.prepare(server,data,True)

    def terminate(self):
        for server,data in self.targets['servers'].items():
            self.prepare(server,data,True,True)

    def shutdown(self):
        for server,data in self.targets['servers'].items():
            self.prepare(server,data)

    def execute(self,type,server,data):
        T = Templator()
        url = "https://github.com/chrislusf/seaweedfs/releases/download/2.49/linux_"+type+".tar.gz"
        print("Installing SeaweedFS")
        self.cmd(data['ip'],'cd /tmp/; wget '+url+"; tar xvf linux_"+type+".tar.gz; mv weed /usr/local/bin/; rm linux_"+type+".tar.gz;",False)

        print("Adding non privileged user for SeaweedFS")
        self.cmd(data['ip'],'getent passwd seaweedfs &>/dev/null && echo "Skipping" ||  mkdir /home/seaweedfs/ && mkdir /home/seaweedfs/master && mkdir /home/seaweedfs/volume && useradd seaweedfs -r -d /home/seaweedfs -s /bin/false && chown -R seaweedfs:seaweedfs /home/seaweedfs/ && chmod -R 700 /home/seaweedfs/',False)

        print('Creating & Starting SeaweedFS master systemd service')
        config = T.genSystemd('master',data['vxlan'],9333,'mdir','peers',9333,self.targets)
        self.cmd(data['ip'],'echo "'+config+'" > /etc/systemd/system/SeaweedFSmaster.service && systemctl enable SeaweedFSmaster && systemctl start SeaweedFSmaster',False)

        print('Creating & Starting SeaweedFS volume systemd service')
        config = T.genSystemd('volume',data['vxlan'],9433,'dir','mserver',9333,self.targets)
        self.cmd(data['ip'],'echo "'+config+'" > /etc/systemd/system/SeaweedFSvolume.service && systemctl enable SeaweedFSvolume && systemctl start SeaweedFSvolume',False)

        print('Creating & Starting SeaweedFS filer systemd service')
        config = T.genSystemd('filer',data['vxlan'],9533,'dir','master',9333,self.targets)
        self.cmd(data['ip'],'echo "'+config+'" > /etc/systemd/system/SeaweedFSfiler.service && systemctl enable SeaweedFSfiler && systemctl start SeaweedFSfiler',False)

    def run(self):
        print("Launching")
        time.sleep(3)
        for server,data in self.targets['servers'].items():
            #Prepare
            self.prepare(server,data)
            print("---",server,"Deploying","---")
            self.execute(self.targets['type'],server,data)
