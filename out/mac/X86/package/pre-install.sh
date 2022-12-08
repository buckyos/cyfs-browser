#!/bin/sh

readonly PLIST="${HOME}/Library/LaunchAgents/com.cyfs.runtime-monitor.plist"
readonly RUNTIME_DIR="${HOME}/Library/Application\ Support/cyfs/services/runtime"


# unload cyfs-runtime monitor task if task is exist
monitor_task_id=`launchctl list | grep com.cyfs.runtime-monitor | grep -v "grep"`
if [ -n ${runtime_monitor_task_id} ]; then
    echo runtime-monitor task status is ${monitor_task_id}.
    echo unload com.cyfs.runtime-monitor.plist.
    /bin/launchctl unload -w ${PLIST}
fi

function kill_process {
    name=$1
    echo kill $name process
    PROCESS=`ps -ef | grep $name | grep -v "grep" | awk '{print $2}'`
    for i in $PROCESS
    do 
        echo "KILL the process $i "
        kill -9 $i
    done
}

function kill_browser_process {
    echo kill CYFS Browser process
    PROCESS=`ps -ef | grep CYFS\ Browser | grep -v "grep" | awk '{print $2}'`
    for i in $PROCESS
    do 
        echo "KILL the process $i "
        kill -9 $i
    done
}

# kill cyfs-runtime process
kill_process 'cyfs-runtime'

# kill ‘CYFS Browser’ process
kill_browser_process

# remove runtime dir if dir exist
echo remove "${RUNTIME_DIR}"
[ -d "${RUNTIME_DIR}" ] && rm -rf "${RUNTIME_DIR}"


# remove plist file if the file is exist
echo remove ${PLIST}
[ -f ${PLIST} ] && rm -rf ${PLIST}


exit 0

