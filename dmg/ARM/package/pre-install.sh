#!/bin/sh

PLIST=${HOME}/Library/LaunchAgents/com.cyfs.runtime-monitor.plist
RUNTIME_DIR=${HOME}/Library/Application\ Support/cyfs/services/runtime

runtime_monitor_task_id=`launchctl list | grep com.cyfs.runtime-monitor | grep -v "grep"`
if [[ -n ${runtime_monitor_task_id} ]]; then
    echo runtime-monitor task status is ${runtime_monitor_task_id}.
    echo unload com.cyfs.runtime-monitor.plist.
    /bin/launchctl unload -w ${PLIST}
else
    echo runtime-monitor task is not running.
    runtime_process_id=`ps -ef | grep cyfs-runtime | grep -v "grep" | awk '{print $2}'`
    if [[ -n ${runtime_process_id} ]]; then
        echo cyfs-runtime pid is $runtime_process_id.
        for id in $runtime_process_id
        do
            kill -9 $id  
            echo "killed pid $id process cyfs-runtime".
        done
    else
        echo cyfs-runtime process is not running, no need kill.
    fi
fi

if [[ -d ${RUNTIME_DIR} ]]; then
    rm -rf ${RUNTIME_DIR}
fi

if [[ -f ${PLIST} ]]; then 
    rm -f ${PLIST}
fi

exit 0
