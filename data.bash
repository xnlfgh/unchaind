#!/bin/bash
set -euxo pipefail

DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"

mkdir $DIR/tmp
cd $DIR/tmp

wget -O sde.bz2 https://www.fuzzwork.co.uk/dump/sqlite-latest.sqlite.bz2
bunzip2 sde.bz2
sqlite3 sde "SELECT solarSystemID,solarSystemName,security FROM mapSolarSystems;" > $DIR/unchaind/data/system.txt
sqlite3 sde "select fromSolarSystemID,toSolarSystemID from mapSolarSystemJumps;" > $DIR/unchaind/data/connection.txt
rm -rf $DIR/tmp
