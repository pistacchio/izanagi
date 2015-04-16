#!/usr/bin/env sh

mkdir -p ~/.izanagi/formulas
mkdir -p ~/.izanagi/bin
mkdir -p ~/.izanagi/cache

wget https://raw.githubusercontent.com/pistacchio/izanagi/master/src/izanagi.py -O ~/.izanagi/bin/izanagi.py
wget https://raw.githubusercontent.com/pistacchio/izanagi/master/src/config -O ~/.izanagi/config
chmod +x ~/.izanagi/bin/izanagi.py
ln -s ~/.izanagi/bin/izanagi.py /usr/local/bin/izanagi

# formula template
mkdir -p ~/.izanagi/formulas/.formula_template/
mkdir -p ~/.izanagi/formulas/.formula_template/skel
wget https://raw.githubusercontent.com/pistacchio/izanagi/master/formulas/.formula_template/install -O ~/.izanagi/formulas/.formula_template/install
chmod +x ~/.izanagi/formulas/.formula_template/install

izanagi update