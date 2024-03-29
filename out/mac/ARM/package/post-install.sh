#!/bin/sh

readonly RUNTIME_DIR="${HOME}/Library/Application Support/cyfs/services/runtime"
readonly TOOLS_DIR="${HOME}/Library/Application Support/cyfs/services/runtime/tools"

readonly BROWSER_DIR="cyber"
readonly BROWSER_EXTENSION_DIR="${HOME}/Library/Application Support/${BROWSER_DIR}/Default/cyfs_extensions"
readonly BROWSER_OLD_EXTENSION_DIR="${HOME}/Library/Application Support/${BROWSER_DIR}/Extensions"

cd "$RUNTIME_DIR"

chmod +x cyfs-runtime
chmod +x ipfs
chmod +x ipfs-proxy
chmod +x enslookup

cd "$TOOLS_DIR"

chmod +x cyfs-client
chmod +x pack-tools

if [ -d "${BROWSER_EXTENSION_DIR}" ]
then
    echo "rm -rf "${BROWSER_EXTENSION_DIR}""
    rm -rf "${BROWSER_EXTENSION_DIR}"
fi

if [ -d "${BROWSER_OLD_EXTENSION_DIR}" ]
then
    echo "rm -rf "${BROWSER_OLD_EXTENSION_DIR}""
    rm -rf "${BROWSER_OLD_EXTENSION_DIR}"
fi

exit 0