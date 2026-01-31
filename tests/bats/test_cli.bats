#!/usr/bin/env bats

setup() {
    if [ -z "$GITMASTERY_BINARY" ]; then
        echo "Error: GITMASTERY_BINARY environment variable is not set"
        echo "Usage: GITMASTERY_BINARY=../../dist/gitmastery bats ."
        exit 1
    fi
    
    TEST_TEMP_DIR="$(mktemp -d)"
}

teardown() {
    if [ -n "$TEST_TEMP_DIR" ] && [ -d "$TEST_TEMP_DIR" ]; then
        rm -rf "$TEST_TEMP_DIR"
    fi
}

# Helper function to run the gitmastery binary
run_gitmastery() {
    run $GITMASTERY_BINARY "$@"
}

# Tests for basic commands
@test "help output contains all main commands" {
    run_gitmastery --help

    echo
    
    [ "$status" -eq 0 ]
    [[ "$output" == *"check"* ]]
    [[ "$output" == *"download"* ]]
    [[ "$output" == *"progress"* ]]
    [[ "$output" == *"setup"* ]]
    [[ "$output" == *"verify"* ]]
    [[ "$output" == *"version"* ]]
}

@test "version output format is correct" {
    run_gitmastery version
    
    [ "$status" -eq 0 ]
    [[ "$output" =~ "Git-Mastery app is" ]]
}
