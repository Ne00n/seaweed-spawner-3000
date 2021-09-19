import requests, sys

#python3 test.py localip file
#Request fid
r = requests.get('http://'+sys.argv[1]+':9333/dir/assign')
if (r.status_code != 200): sys.exit()
fileDetails = r.json()
print(fileDetails)
#Upload file
files = {'file':(sys.argv[2], open(sys.argv[2], 'rb'))}
r = requests.post("http://"+fileDetails['url']+"/"+fileDetails['fid'], files=files)
if (r.status_code != 201): sys.exit()
response = r.json()
print(response)
#Retrieve file
r = requests.get("http://"+fileDetails['url']+"/"+fileDetails['fid'])
if (r.status_code != 200): sys.exit()
print(r.content)
