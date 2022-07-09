#!/bin/sh

APPLICATIONSUPPORT="${HOME}/Library/Application Support"
RUNTIME_DATA_PATH=cyfs
BROWSER_DATA_PATH=cyber
PLIST=${HOME}/Library/LaunchAgents/com.cyfs.runtime-monitor.plist
BROWSER_APP_PATH="${HOME}/Applications"

function delete_user_data {
    pushd "${APPLICATIONSUPPORT}"
    echo "begin delete application user data"
    if [[ -d ${RUNTIME_DATA_PATH} ]]; then
        sudo /bin/rm -rf ${RUNTIME_DATA_PATH}
    fi

    if [[ -d ${BROWSER_DATA_PATH} ]]; then
        sudo /bin/rm -rf ${BROWSER_DATA_PATH}
    fi
    echo "end delete application user data"
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
    if [[ -d ${BROWSER_APP} ]]; then
        sudo /bin/rm -rf ${BROWSER_APP}
        echo delete ${BROWSER_APP}
    else
        echo ${BROWSER_APP} is not exist.
    fi
}

function remove_browser_application {
    pushd ${BROWSER_APP_PATH}
    if [[ -d "Cyfs Browser.app" ]]; then
        sudo /bin/rm -rf "Cyfs Browser.app"
        echo delete "Cyfs Browser.app"
    else
        echo "Cyfs Browser.app" is not exist.
    fi
    popd
}

## Check if need uninstall application
echo "--------------------------------------------------------------------------"
echo "--------------------------------------------------------------------------"
while true; do
    read -p "You are uninstall Cyfs Browser application. Are you sure [Y/N]" answer
    case $answer in 
    Y | y | yes | YES) 
        echo "begin uninstall application"
        break;;
    N | n | no | NO)
        echo "cancel uninstall Cyfs Browser application user"
        exit 0;;
    *) echo "Please answer yes or no";;
    esac
done
echo "---------------------------"

browser_process_id=`ps -ef | grep "Cyfs Browser" | grep -v "grep" | awk '{print $2}'`
if [[ -n ${browser_process_id} ]]; then
    echo Cyfs Browser is runing, please close the application.
    echo Cyfs Browser pid is $browser_process_id.
    sleep 5
    exit 0
fi

sleep 2

## Remove application
remove_browser_application

## Check delete application user data
while true; do
    read -p "delete application user data [Y/N]" answer
    case $answer in 
    Y | y | yes | YES) 
        echo "delete application user data"
        delete_user_data
        break;;
    N | n | no | NO)
        echo "no need delete application user data"
        delete_runtime_user_data
        break;;
    *) echo "Please answer yes or no";;
    esac
done
echo "--------------------------"

## forget com.cyfs.browser.package
package_exist=`pkgutil --pkgs-plist | grep "com.cyfs.browser.package"`
if [[ -n ${package_exist} ]]; then
    sudo /usr/sbin/pkgutil --forget com.cyfs.browser.package
fi

echo "end uninstall Cyfs Browser application"
echo "uninstall Cyfs Browser finished"
echo "--------------------------------------------------------------------------"
echo "--------------------------------------------------------------------------"
exit 0