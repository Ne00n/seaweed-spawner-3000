from Class.seaweed import SeaweedFS
import sys
print("SeaweedFS Spawner 3000")
config = "hosts.json"
if len(sys.argv) > 2:
    config = sys.argv[2]
seaweed = SeaweedFS(config)
if len(sys.argv) == 1:
    print("build, shutdown, clean")
elif sys.argv[1] == "build":
    seaweed.run()
elif sys.argv[1] == "shutdown":
    seaweed.shutdown()
elif sys.argv[1] == "terminate":
    seaweed.terminate()
elif sys.argv[1] == "clean":
    seaweed.clean()
