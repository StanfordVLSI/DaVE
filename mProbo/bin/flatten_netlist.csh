#!/bin/csh

set filename = $1
shift 
spnet $* $filename
