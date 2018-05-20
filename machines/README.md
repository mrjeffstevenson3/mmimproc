Docker
======


Build a container from the Dockerfile in the mmpa directory, for example to test 
adjustments, and tag it as "jasper/mmpa".
```
docker build -t jasper/mmpa mmpa
```

Download the latest version of the jasper/mmp container:
```
docker pull jasper/mmpa
```

Start the container "jasper/mmpa" with the bash command in interactive mode 
("-it"). The -v arguments specify directories to share. I recommend to share 
data and code directories.
```
docker run -it \
-v /diskArray/data:/diskArray/data \
-v /home/jasperb/Projects:/home/jasperb/Projects \
jasper/mmpa /bin/bash
```



