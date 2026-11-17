#!/bin/sh
printf 'cwd=%s GOTOOLCHAIN=%s GOVERSION=%s args=' "$PWD" "$GOTOOLCHAIN" "$GOVERSION" >> /tmp/tracera-osv-native-proof-20261017/go-calls.log
printf '%s ' "$@" >> /tmp/tracera-osv-native-proof-20261017/go-calls.log
printf '\n' >> /tmp/tracera-osv-native-proof-20261017/go-calls.log
/usr/local/go/bin/go version >> /tmp/tracera-osv-native-proof-20261017/go-calls.log 2>&1
exec /usr/local/go/bin/go "$@"
