import {
    sendWithPromise
} from 'chrome://resources/js/cr.m.js';
import {
    $
} from 'chrome://resources/js/util.m.js';

var UpdateIntervalID;
let isFirstRun = undefined;
let currentRuntimeBindStatus = undefined;
let lastRuntimeBindStatus = undefined;

function returnRuntimePorcessStatus(status) {
    if (status == true) {
        console.log(`runtime process status is running }`);
        // window.location.href = "cyfs://static/browser.html";
        let target_url = loadTimeData.getStringF('browser_url');
        if (isFirstRun) {
            // browser_url = browser_url + '?first=true';
            target_url = loadTimeData.getStringF('guide_url');
        }
        window.location.href = target_url;
        if (UpdateIntervalID)
            clearInterval(UpdateIntervalID);
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

    const getRuntimeBindingStatus = function () {
        sendWithPromise('getRuntimeBindStatus').then(status => {
            console.log(`current runtime bind status: ${status}`);
            currentRuntimeBindStatus = status;
        });
    };
    getRuntimeBindingStatus();

    const getRuntimeBindStatusFromProfile = function () {
        sendWithPromise('getRuntimeBindStatusFromProfile').then(status => {
            console.log(`last runtime bind status: ${status}`);
            lastRuntimeBindStatus = status;
        });
    };
    getRuntimeBindStatusFromProfile();

    const getRuntimeProxystatus = function() {
        sendWithPromise('getRuntimeProxystatus').then(status => {
            console.log(`runtime proxy status: ${status}`);
        })
    }
    getRuntimeProxystatus();

    const getRuntimeRunningStatus = function () {
        sendWithPromise('getRuntimeProcessStatus').then(status => {
            returnRuntimePorcessStatus(status);
        });
    };
    getRuntimeRunningStatus();
    UpdateIntervalID = setInterval(getRuntimeRunningStatus, 200);
}

function main() {
    console.log(`main`);
    startUpdateRequests();
}

document.addEventListener('DOMContentLoaded', main);
