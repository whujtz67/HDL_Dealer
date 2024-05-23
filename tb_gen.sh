#!/bin/bash
if [ "$1" = "-n" ]; then
    python3 src/main.py -fl filelist.f --top TestTop_fullSys_1Core --nodpi -v
else
    python3 testbench_gen.py -f TestTop.v --top TestTop_fullSys_1Core --nodpi -v
fi


