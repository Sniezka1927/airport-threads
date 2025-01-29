#!/bin/bash

pgrep python3 | xargs -r kill -9
pgrep pytest | xargs -r kill -9