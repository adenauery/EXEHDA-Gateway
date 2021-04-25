#!/bin/sh

random_hash () {
	echo $(cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 8 | head -n 1)"-"$(cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 4 | head -n 1)"-"$(cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 4 | head -n 1)"-"$(cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 4 | head -n 1)"-"$(cat /dev/urandom | tr -dc 'a-f0-9' | fold -w 12 | head -n 1);
}
