#!/bin/bash

ARG=$1

if grep -q "$ARG:" utils/config.yaml; then

  VALUE=$(grep "$ARG:" utils/config.yaml | cut -d':' -f2)
  VALUE=$(echo "$VALUE" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

  sed -zi "s/\('''\)[^']*\('''\)/\1$1\2/g" scrapy/spider_decanter.py
  scrapy runspider scrapy/spider_decanter.py -a limit=$VALUE

  sed -zi "s/\('''\)[^']*\('''\)/\1$1\2/g" scrapy/json_parser.py
  python scrapy/json_parser.py

else

  echo "Error: $ARG is not a valid country in this project."

fi

sleep 10
