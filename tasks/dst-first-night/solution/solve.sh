#!/bin/bash
set -euo pipefail
echo "DST has no validated successful reference policy in this release. Refusing to fabricate an oracle reward." >&2
exit 2
