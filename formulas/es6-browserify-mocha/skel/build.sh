#!/bin/bash

function compile {
    TEMPDIR=`mktemp -d /tmp/es6.XXXX`

    if [ ! -d "dist" ]; then
        mkdir dist
    fi

    if [ ! -d "tests" ]; then
        mkdir tests
    fi

    babel src --out-dir $TEMPDIR

    if [[ $* == *--browser* ]]; then
        browserify $TEMPDIR/app.js  --debug -o dist/app.js
    else
        cp -r $TEMPDIR/* dist/
    fi

    for FILE in $TEMPDIR/tests/*test*.js; do
        browserify $FILE --debug -o ./tests/$(basename $FILE)
    done
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