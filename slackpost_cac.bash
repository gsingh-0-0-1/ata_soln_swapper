#!/bin/sh
curl -d "text=\`Applying solutions cached in $1\`" -d "channel=${ATACHANNEL}" -H "Authorization: Bearer ${ATATOKEN}" -X POST https://slack.com/api/chat.postMessage
echo ""

