#!/bin/bash

function compile {
    TEMPDIR=`mktemp -d /tmp/es6.XXXX`

    if [ ! -d "dist" ]; then
        mkdir dist
    fi

    babel src --out-dir $TEMPDIR
    browserify $TEMPDIR/app.js  --debug -o dist/app.js

    cp -r $TEMPDIR/tests .
}

if [[ $* == *--clean* ]]; then
    rm -rf test dist
    exit 0
fi

if [[ $* != *--no-compile* ]]; then
    compile
fi

if [[ $* == *--watch* ]]; then
    fswatch src ./build.sh
fi

if [[ $* == *--test* ]]; then
    mocha -C tests/*.js
fi

rm -r $TEMPDIR