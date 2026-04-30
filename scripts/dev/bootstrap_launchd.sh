#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-install}"
LABEL="com.genaitaskq.autostart"
LAUNCH_AGENTS_DIR="${HOME}/Library/LaunchAgents"
PLIST_PATH="${LAUNCH_AGENTS_DIR}/${LABEL}.plist"
TEMPLATE_PATH="$(cd "$(dirname "$0")" && pwd)/com.genaitaskq.autostart.plist.template"
WORKDIR="$(cd "$(dirname "$0")/../.." && pwd)"

mkdir -p "${LAUNCH_AGENTS_DIR}"

if [[ "${MODE}" == "uninstall" ]]; then
  launchctl bootout "gui/$(id -u)" "${PLIST_PATH}" >/dev/null 2>&1 || true
  rm -f "${PLIST_PATH}"
  echo "launchd: uninstalled ${LABEL}"
  exit 0
fi

if [[ ! -f "${TEMPLATE_PATH}" ]]; then
  echo "launchd: template not found: ${TEMPLATE_PATH}" >&2
  exit 1
fi

DOCKER_BIN="$(command -v docker || true)"
if [[ -z "${DOCKER_BIN}" ]]; then
  echo "launchd: docker command not found." >&2
  exit 1
fi

sed \
  -e "s#__WORKDIR__#${WORKDIR}#g" \
  -e "s#/usr/local/bin/docker#${DOCKER_BIN}#g" \
  "${TEMPLATE_PATH}" > "${PLIST_PATH}"

launchctl bootout "gui/$(id -u)" "${PLIST_PATH}" >/dev/null 2>&1 || true
launchctl bootstrap "gui/$(id -u)" "${PLIST_PATH}"
launchctl enable "gui/$(id -u)/${LABEL}"
launchctl kickstart -k "gui/$(id -u)/${LABEL}"

echo "launchd: installed ${LABEL} at ${PLIST_PATH}"
