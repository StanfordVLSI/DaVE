#!/bin/bash
if [ "$1" = "vcs" ]; then
  vcs *.v +protect -full64
elif [ "$1" = "ncsim" ]; then
  ncprotect -fcreate *.v
  rm ncprotect.log
else
  echo "Choose a correct simulator for compiling primitive models"
fi
