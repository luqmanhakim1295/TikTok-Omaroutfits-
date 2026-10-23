#!/bin/bash
# usage: sheet.sh clip outdir step cols
clip=$1; out=$2; step=$3; cols=$4; mkdir -p $out
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $clip)
i=0; for t in $(seq 1 $step ${dur%.*}); do i=$((i+1)); ffmpeg -y -loglevel error -ss $t -i $clip -frames:v 1 -vf "scale=144:256,drawgrid=w=36:h=256:t=1:c=yellow@0.4,drawbox=x=71:y=0:w=2:h=256:color=red:t=fill,drawtext=text='$t':x=2:y=2:fontsize=16:fontcolor=white:box=1:boxcolor=black" $out/$(printf %03d $i).jpg; done
ffmpeg -y -loglevel error -i $out/%03d.jpg -vf tile=${cols}x$(( (i+cols-1)/cols )) -frames:v 1 $out.jpg
