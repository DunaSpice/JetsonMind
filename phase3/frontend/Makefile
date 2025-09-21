CC=gcc
CFLAGS=-Wall -Wextra -std=c99
LIBS=-lcurl -ljson-c
TARGET=phase3_frontend
SRC=main.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LIBS)

clean:
	rm -f $(TARGET)

install:
	sudo apt-get update
	sudo apt-get install -y libcurl4-openssl-dev libjson-c-dev

.PHONY: all clean install
