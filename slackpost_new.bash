#!/bin/sh
curl -F file=@./observation.png -F channels=$ATACHANNEL -H "Authorization: Bearer ${ATATOKEN}" https://slack.com/api/files.upload
echo ""
curl -F file=@./calibration.png -F channels=$ATACHANNEL -H "Authorization: Bearer ${ATATOKEN}" https://slack.com/api/files.upload
echo ""

curl -d "text=\`Solutions applied and cached in $1\`" -d "channel=${ATACHANNEL}" -H "Authorization: Bearer ${ATATOKEN}" -X POST https://slack.com/api/chat.postMessage
echo ""

