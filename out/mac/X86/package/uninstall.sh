#!/bin/sh

APPLICATIONSUPPORT="${HOME}/Library/Application Support"
RUNTIME_DATA_PATH=cyfs
BROWSER_DATA_PATH=CYFS_Browser
PLIST=${HOME}/Library/LaunchAgents/com.cyfs.runtime-monitor.plist
BROWSER_APP_PATH="${HOME}/Applications"
BROWSER_APP="CYFS Browser.app"

function delete_user_data {
    pushd "${APPLICATIONSUPPORT}"
    echo "Begin delete application user data"
    if [[ -d ${RUNTIME_DATA_PATH} ]]; then
        sudo /bin/rm -rf ${RUNTIME_DATA_PATH}
    fi

    if [[ -d ${BROWSER_DATA_PATH} ]]; then
        sudo /bin/rm -rf ${BROWSER_DATA_PATH}
    fi
    echo "End delete application user data"
    popd
}

function delete_runtime_user_data {
    pushd "${APPLICATIONSUPPORT}"
    if [[ -d ${RUNTIME_DATA_PATH}/services/runtime ]]; then
        sudo /bin/rm -rf ${RUNTIME_DATA_PATH}/services/runtime
    fi
    popd
}

function remove_browser_application {
    pushd ${BROWSER_APP_PATH}
    echo "Begin delete application"
    if [[ -d "${BROWSER_APP}" ]]; then
        sudo /bin/rm -rf "${BROWSER_APP}"
        echo delete ${BROWSER_APP}
    else
        echo "${BROWSER_APP}" is not exist.
    fi
    echo "End delete application"
    popd
}


## Check if need uninstall application
echo "--------------------------------------------------------------------------"
echo "--------------------------------------------------------------------------"
while true; do
    read -p "You are uninstall CYFS Browser application. Are you sure [Y/N]? " answer
    case $answer in 
    Y | y | yes | YES) 
        echo "Begin uninstall application"
        break;;
    N | n | no | NO)
        echo "cancel uninstall CYFS Browser application user"
        exit 0;;
    *) echo "Please answer yes or no";;
    esac
done
echo "--------------------------------------------------------------------------"

browser_process_id=`ps -ef | grep "CYFS Browser" | grep -v "grep" | awk '{print $2}'`
if [[ -n ${browser_process_id} ]]; then
    echo CYFS Browser process is runing, please close the application.
    echo CYFS Browser pid is $browser_process_id.
    sleep 5
    exit 0
fi

sleep 2

## Remove application
remove_browser_application

## Check delete application user data
while true; do
    read -p "Delete application user data [Y/N]? " answer
    case $answer in 
    Y | y | yes | YES) 
        echo "Delete application user data"
        delete_user_data
        break;;
    N | n | no | NO)
        echo "No need delete application user data"
        delete_runtime_user_data
        break;;
    *) echo "Please answer yes or no";;
    esac
done
echo "--------------------------------------------------------------------------"

## forget com.cyfs.browser.package
package_exist=`pkgutil --pkgs-plist | grep "com.cyfs.browser.package"`
if [[ -n ${package_exist} ]]; then
    sudo /usr/sbin/pkgutil --forget com.cyfs.browser.package
fi

echo "End uninstall CYFS Browser application"
echo "Uninstall CYFS Browser finished"
echo "--------------------------------------------------------------------------"
echo "--------------------------------------------------------------------------"
exit 0