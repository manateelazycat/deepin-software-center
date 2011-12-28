#!/bin/sh

while read line; do sed -i /$line/d */*/*.txt */*.txt; done < test.txt 
