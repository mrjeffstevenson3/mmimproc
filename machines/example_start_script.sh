## This is an example script to start a container while linking your data and code
docker run -it \
-v /diskArray/data:/diskArray/data \
-v /home/jasperb/Projects:/home/jasperb/Projects \
jasper/mmpa /bin/bash
