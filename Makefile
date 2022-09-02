IDIR =./include
CC=gcc
CFLAGS=-g -Wall -O2 -Wno-unused-function -I$(IDIR)

SDIR=./src/

LIBS=-lm

all: template

template: $(SDIR)template.c
	$(CC) $(CFLAGS) $^ -o $@ -lz -lm -g


