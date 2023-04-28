import {
    sendWithPromise
} from 'chrome://resources/js/cr.m.js';

sendWithPromise('getRuntimeBindStatus').then(status => {
    console.log(`runtime bind status: ${status}`);
    window.isBind = status;
});