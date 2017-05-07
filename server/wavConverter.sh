#!/bin/bash

i_name=$1
o_name="${i_name}.wav"
ffmpeg -i "${i_name}" "${o_name}" -y >/dev/null 2>&1
mv -f "${o_name}" "${i_name}"
