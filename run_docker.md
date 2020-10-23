# Build

```
docker build -t taxbrain-test ./
```

# Run

```
docker run -v `pwd`:/home/Tax-Brain -it taxbrain-test /bin/bash
```

# Test

```
docker run -v .:/home/Tax-Brain -i taxbrain-test py.test taxbrain
```

# CS Tests

```
docker run -v .:/home/Tax-Brain -i taxbrain-test py.test cs-config -v
```
