#!/bin/sh
curl https://ocaml.org/releases 2>/dev/null |grep "/releases/" |head -n1 |sed -e 's,.*/releases/,,;s,".*,,'
