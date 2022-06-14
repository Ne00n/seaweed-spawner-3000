import subprocess, time, json, re
from Class.templator import Templator

class SeaweedFS:

    targets = []

    def __init__(self,config="hosts.json"):
        print("Loading",config)
        with open(config) as handle:
            self.targets = json.loads(handle.read())

    def cmd(self,server,command):
        cmd = ['ssh','root@'+server,command]
        for run in range(4):
            try:
                p = subprocess.run(cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
                if p.returncode != 0:
                    print("Warning got returncode",p.returncode,"on",server)
                    print("Error:",p.stderr.decode('utf-8'))
                if p.returncode != 255: return [p.stdout.decode('utf-8'),p.stderr.decode('utf-8')]
            except Exception as e:
                print("Error:",e)
            print("Retrying",cmd,"on",server)
            time.sleep(random.randint(5, 15))

    def prepare(self,server,data,delete=False,terminate=False):
        print("---",server,"Preparing","---")
        #Fetch old configs
        files = self.cmd(data['ip'],'ls /etc/systemd/system/')[0]
        #Parse configs
        parsed = re.findall("^SeaweedFS[A-Za-z0-9.-]+",files, re.MULTILINE)
        #Disable old configs
        for service in parsed:
            print("Stopping "+service)
            self.cmd(data['ip'],'systemctl stop '+service+' && systemctl disable '+service)
            if delete: self.cmd(data['ip'],'rm /etc/systemd/system/'+service)
        if terminate: self.cmd(data['ip'],'userdel -r seaweedfs')


    def clean(self):
        for server,data in self.targets['servers'].items():
            self.prepare(server,data,True)

    def terminate(self):
        for server,data in self.targets['servers'].items():
            self.prepare(server,data,True,True)

    def shutdown(self):
        for server,data in self.targets['servers'].items():
            self.prepare(server,data)

    def execute(self,server,data):
        T = Templator()
        url = "https://github.com/chrislusf/seaweedfs/releases/download/"+self.targets['version']+"/linux_"+data['type']+".tar.gz"
        print("Installing SeaweedFS")
        self.cmd(data['ip'],'cd /tmp/; wget '+url+"; tar xvf linux_"+data['type']+".tar.gz; mv weed /usr/local/bin/; rm linux_"+data['type']+".tar.gz;")

        print("Adding non privileged user for SeaweedFS")
        self.cmd(data['ip'],'getent passwd seaweedfs &>/dev/null && echo "Skipping" ||  mkdir /home/seaweedfs/ && mkdir /home/seaweedfs/master && mkdir /home/seaweedfs/volume && useradd seaweedfs -r -d /home/seaweedfs -s /bin/false && chown -R seaweedfs:seaweedfs /home/seaweedfs/ && chmod -R 700 /home/seaweedfs/')

        print('Creating & Starting SeaweedFS master systemd service')
        config = T.genSystemd('master',data['vpn'],9333,'mdir','peers',9333,self.targets)
        self.cmd(data['ip'],'echo "'+config+'" > /etc/systemd/system/SeaweedFSmaster.service && systemctl enable SeaweedFSmaster && systemctl start SeaweedFSmaster')

        print('Creating & Starting SeaweedFS volume systemd service')
        config = T.genSystemd('volume',data['vpn'],9433,'dir','mserver',9333,self.targets,data['dc'],data['rack'])
        self.cmd(data['ip'],'echo "'+config+'" > /etc/systemd/system/SeaweedFSvolume.service && systemctl enable SeaweedFSvolume && systemctl start SeaweedFSvolume')

        print('Creating & Starting SeaweedFS filer systemd service')
        config = T.genSystemd('filer',data['vpn'],9533,'dir','master',9333,self.targets)
        self.cmd(data['ip'],'echo "'+config+'" > /etc/systemd/system/SeaweedFSfiler.service && systemctl enable SeaweedFSfiler && systemctl start SeaweedFSfiler')

        if "mount" in data:
            print('Creating & Starting SeaweedFS mount systemd service')
            config = T.genSystemd('mount',data['vpn'],9533,'dir','master',0,self.targets,data['mount']['dir'],data['mount']['filer'])
            self.cmd(data['ip'],'echo "'+config+'" > /etc/systemd/system/SeaweedFSmount.service && systemctl enable SeaweedFSmount && systemctl start SeaweedFSmount')

    def run(self):
        print("Launching")
        time.sleep(3)
        for server,data in self.targets['servers'].items():
            #Prepare
            self.prepare(server,data)
            print("---",server,"Deploying","---")
            self.execute(server,data)
