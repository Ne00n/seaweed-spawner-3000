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

    def prepare(self,server,data,delete=False):
        print("---",server,"Preparing","---")
        #Fetch old configs
        files = self.cmd(data['ip'],'ls /etc/systemd/system/',True)
        #Parse configs
        parsed = re.findall("^SeaweedFS[A-Za-z0-9.]+",files, re.MULTILINE)
        #Disable old configs
        for service in parsed:
            print(server,"Stopping "+service)
            self.cmd(data['ip'],'systemctl stop '+service+' && systemctl disable '+service,False)
        if delete: self.cmd(data['ip'],'rm /etc/systemd/system/'+service,False)

    def clean(self):
        for server,data in self.targets['servers'].items():
            self.prepare(server,data,True)

    def shutdown(self):
        for server,data in self.targets['servers'].items():
            self.prepare(server,data)

    def execute(self,type,server,data):
        T = Templator()
        url = "https://github.com/chrislusf/seaweedfs/releases/download/2.49/linux_"+type+".tar.gz"
        print(server,"Installing SeaweedFS")
        self.cmd(data['ip'],'cd /tmp/; wget '+url+"; tar xvf linux_"+type+".tar.gz; mv weed /usr/local/bin/; rm linux_"+type+".tar.gz;",False)

        print(server,"Adding non privileged user for SeaweedFS")
        self.cmd(data['ip'],'getent passwd seaweedfs &>/dev/null && echo "Skipping" ||  mkdir /home/seaweedfs/ && useradd seaweedfs -r -d /home/seaweedfs -s /bin/false && chown -R seaweedfs:seaweedfs /home/seaweedfs/ && chmod -R 700 /home/seaweedfs/',False)

        print(server,'Creating & Starting SeaweedFS master systemd service')
        config = T.genSystemd('master',data['vxlan'],9333,'mdir','peers',9333,self.targets)
        self.cmd(data['ip'],'echo "'+config+'" > /etc/systemd/system/SeaweedFSmaster.service && systemctl enable SeaweedFSmaster && systemctl start SeaweedFSmaster',False)

    def run(self):
        print("Launching")
        time.sleep(3)
        for server,data in self.targets['servers'].items():
            #Prepare
            self.prepare(server,data)
            print("---",server,"Deploying","---")
            self.execute(self.targets['type'],server,data)