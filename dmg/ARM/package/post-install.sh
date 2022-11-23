#!/bin/sh

readonly RUNTIME_DIR="${HOME}/Library/Application Support/cyfs/services/runtime"
readonly TOOLS_DIR="${HOME}/Library/Application Support/cyfs/services/runtime/tools"

readonly BROWSER_EXTENSION_DIR="${HOME}/Library/Application Support/cyber/Default/cyfs_extensions"

cd "$RUNTIME_DIR"

chmod +x cyfs-runtime
chmod +x ipfs
chmod +x ipfs-proxy

cd "$TOOLS_DIR"

chmod +x cyfs-client
chmod +x pack-tools

if [ -d "${BROWSER_EXTENSION_DIR}" ]
then
    rm -rf "${BROWSER_EXTENSION_DIR}"
fi

exit 0