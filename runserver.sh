#!/usr/bin/env bash
title1="FLASK_APP"
title2="CELERY_WORKER"
title3="FLOWER"

cmd1="./run_app.sh"
cmd2="./run_celery.sh"
cmd3="./run_flower.sh"

gnome-terminal --tab --title="$title1" --command="bash -c '$cmd1; $SHELL'" \
               --tab --title="$title2" --command="bash -c '$cmd2; $SHELL'" \
               --tab --title="$title3" --command="bash -c '$cmd3; $SHELL'"
