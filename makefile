#!/bin/bash

run:
	uvicorn app.main:app

update:
	pipreqs .

build:
	podman build -t pix-id-base:latest -f Dockerfile.base . && podman build -t pix-id:v1 .

up:
	podman compose up -d