# seaweed-spawner-3000

I better replicate mah storage expansion for: https://github.com/Ne00n/pipe-builder-3000/ </br>
Configures [SeaweedFS](https://github.com/chrislusf/seaweedfs) on all nodes (master/volume/filer) including HA

You need at least 3 nodes<br />
Tested on Debian 10 and Ubuntu 20.04 with systemd.

**Dependencies**<br />
none

**Prepare**<br />
Rename hosts.example.json to hosts.json and fill it up

**Usage**<br />
Builds or Updates the SeaweedFS cluster<br />
```
python3 seaweed.py build
```
Shutdown of all SeaweedFS instances<br />
```
python3 seaweed.py shutdown
```
Removes all SeaweedFS instances<br />
```
python3 seaweed.py clean
```
Terminates all SeaweedFS instances + data<br />
```
python3 seaweed.py terminate
```
