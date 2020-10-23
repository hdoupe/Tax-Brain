# Build

```
docker build -t taxbrain-test ./
```

# Run

Using -v maps your local directory to the directory in the Docker container. So, if you change your local files, they will be updated in the running container, too. This makes it easy to use VS Code on your local directory to develop in a Docker container.

Also, if you have the PUF file in your local directory, _don't push the docker image anywhere public!_

```
docker run -v `pwd`:/home/Tax-Brain -it taxbrain-test /bin/bash
```

# Test

```
docker run -v `pwd`:/home/Tax-Brain -i taxbrain-test py.test taxbrain
```

# CS Tests

```
docker run -v `pwd`:/home/Tax-Brain -i taxbrain-test py.test cs-config -v
```
