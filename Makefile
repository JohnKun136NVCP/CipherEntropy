PROJECT_ROOT := $(CURDIR)
PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
CC ?= gcc

CRYPTO_DIR := src/crypto
REQ_FILE := requirements.txt

UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Darwin)
SHARED_EXT := dylib
SHARED_FLAGS := -dynamiclib -O2
else
SHARED_EXT := so
SHARED_FLAGS := -shared -fPIC -O2
endif

DES_LIB := $(CRYPTO_DIR)/libdes.$(SHARED_EXT)
RC4_LIB := $(CRYPTO_DIR)/librc4.$(SHARED_EXT)

.PHONY: all build libs des rc4 requirements install run clean help

all: build

build: libs

libs: des rc4

des: $(DES_LIB)

rc4: $(RC4_LIB)

$(DES_LIB): $(CRYPTO_DIR)/des.c $(CRYPTO_DIR)/des_tables.c $(CRYPTO_DIR)/des.h $(CRYPTO_DIR)/des_tables.h
	$(CC) $(SHARED_FLAGS) -o $@ $(CRYPTO_DIR)/des.c $(CRYPTO_DIR)/des_tables.c

$(RC4_LIB): $(CRYPTO_DIR)/rc4.c $(CRYPTO_DIR)/rc4.h
	$(CC) $(SHARED_FLAGS) -o $@ $(CRYPTO_DIR)/rc4.c

requirements:
	$(PIP) install -r $(REQ_FILE)

install: requirements

run: build
	$(PYTHON) main.py

clean:
	rm -f $(DES_LIB) $(RC4_LIB)
	rm -rf __pycache__ src/__pycache__ src/*/__pycache__ src/*/*/__pycache__

help:
	@printf '%s\n' \
		'Available targets:' \
		'  make build         Build the shared libraries in src/crypto' \
		'  make des           Build only libdes' \
		'  make rc4           Build only librc4' \
		'  make requirements  Install Python dependencies from requirements.txt' \
		'  make run           Build libraries and run main.py' \
		'  make clean         Remove build artifacts'

