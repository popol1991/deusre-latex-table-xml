#! /bin/sh

for file in `ls data/*/*.html`
do
    echo $file;
    python convert.py $file > $file.xml;
done
