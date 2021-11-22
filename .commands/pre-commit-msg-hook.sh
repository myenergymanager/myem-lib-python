#!/bin/bash

MESSAGE_FILE="$1"

if ! grep -qE "[A-Z]+-[0-9]+" "$MESSAGE_FILE";
then
    echo "Your commit message format must contain a JIRA task ID example PBK-1"
    exit 1
fi

if ! grep -qE "#time " "$MESSAGE_FILE";
then
    echo "Your commit message format must be contain the tag #time (check how to use it in the JIRA smart commits page)"
    exit 1
fi

if ! grep -qE "#comment " "$MESSAGE_FILE";
then
    echo "Your commit message format must be contain the tag #comment (check how to use it in the JIRA smart commits page)"
    exit 1
fi

exit 0
