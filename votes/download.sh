#!/usr/bin/env bash

set -o errexit
aws s3 sync s3://dwellingofduels-static-site/voting-form ./files