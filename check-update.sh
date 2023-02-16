#!/bin/sh
curl https://ocaml.org/releases 2>/dev/null |grep "/releases/[0-9\.]*\"" |head -n1 |sed -e 's,.*/releases/,,;s,".*,,'
