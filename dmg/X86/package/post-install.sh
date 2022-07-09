#!/bin/sh

# PLIST=${HOME}/Library/LaunchAgents/com.cyfs.runtime-monitor.plist
# current_user=${USER}
# current_user_path=${HOME}
# user=${current_user_path:7}
# echo user ${user}
# whoami=whoami
# echo current user name = ${current_user}
# echo current user path = ${current_user_path}

# if [ -f ${PLIST} ]; then
#     sed -i '' 's/whoami/'${user}'/g' ${PLIST}
# 	echo /bin/launchctl load -w ${PLIST}

#     chmod 600 ${PLIST}
# 	/bin/launchctl load -w ${PLIST}

# 	runtime_process_id=`ps -ef | grep cyfs-runtime | grep -v "grep" | awk '{print $2}'`
#     if [[ -n ${runtime_process_id} ]]; then
#         echo cyfs-runtime pid is running , pid is $runtime_process_id.
#     else
#         echo cyfs-runtime process is not running, please check.
#     fi
# fi

exit 0