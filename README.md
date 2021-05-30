# seaweed-spawner-3000

I better replicate mah storage expansion for: https://github.com/Ne00n/pipe-builder-3000/ </br>
Configures SeaweedFS on all nodes (master/volume/filer) including HA

**Dependencies**<br />
none

**Prepare**<br />
Rename hosts.example.json to hosts.json and fill it up

**Examples**<br />

/etc/hosts<br />
```
bla.bla.bla.bla    Server1
bla.bla.bla.bla    Server2
bla.bla.bla.bla    Server3
```

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
