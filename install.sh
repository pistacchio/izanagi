#!/usr/bin/env sh

mkdir -p ~/.izanagi/formulas
mkdir -p ~/.izanagi/bin
wget https://raw.githubusercontent.com/pistacchio/izanagi/master/src/izanagi.py -O ~/.izanagi/bin/izanagi.py
chmod +x ~/.izanagi/bin/izanagi.py
ln -s ~/.izanagi/bin/izanagi.py /usr/local/bin/izanagi

