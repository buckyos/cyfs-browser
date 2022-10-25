import {
    sendWithPromise
} from 'chrome://resources/js/cr.m.js';
import {
    $
} from 'chrome://resources/js/util.m.js';

var UpdateProcessStatusIntervalID;
var UpdateProxyStatusIntervalID;
let isFirstRun = undefined;
let proxyServerReady = false;


const returnRuntimeProxystatus = function(status) {
    if (status == true) {
        proxyServerReady = true;
        console.log(`runtime proxy server ready: ${status}`);
        if (UpdateProxyStatusIntervalID) {
            clearInterval(UpdateProxyStatusIntervalID);
        }
    } else {
        console.log(`runtime proxy server is not ready, please wait`);
    }
}

function returnRuntimePorcessStatus(status) {
    if (status == true && proxyServerReady == true) {
        console.log(`runtime process status is running }`);
        let target_url = loadTimeData.getStringF('browser_url');
        if (isFirstRun) {
            target_url = loadTimeData.getStringF('guide_url');
        }
        window.location.href = target_url;
        if (UpdateProcessStatusIntervalID)
            clearInterval(UpdateProcessStatusIntervalID);
    } else {
        console.log(`runtime process is not running, please wait`);
    }
};

function startUpdateRequests() {
    const getFirstRunStatus = function () {
        sendWithPromise('getRuntimeFirstRunningStatus').then(status => {
            console.log(`runtime first run status: ${status}`);
            isFirstRun = status;
        });
    };
    getFirstRunStatus();

    const getRuntimeProxystatus = function() {
        sendWithPromise('getRuntimeProxystatus').then(status => {
            returnRuntimeProxystatus(status);
        })
    }
    getRuntimeProxystatus();
    UpdateProxyStatusIntervalID = setInterval(getRuntimeProxystatus, 200);

    const getRuntimeRunningStatus = function () {
        sendWithPromise('getRuntimeProcessStatus').then(status => {
            returnRuntimePorcessStatus(status);
        });
    };
    getRuntimeRunningStatus();
    UpdateProcessStatusIntervalID = setInterval(getRuntimeRunningStatus, 200);
}

function main() {
    console.log(`main`);
    startUpdateRequests();
}

document.addEventListener('DOMContentLoaded', main);
