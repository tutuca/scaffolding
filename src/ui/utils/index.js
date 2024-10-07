import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

export function randomChoice(arr) {
    return arr[Math.floor(arr.length * Math.random())];
}

export function cleanParams(params) {
    const keysForDel = [];
    for (const key in params) {
        if (Object.hasOwnProperty.call(params, key)) {
            const v = params[key];
            if (v === undefined || v === null || v === "") {
                keysForDel.push(key);
            }
        }
    }
    keysForDel.forEach((k) => {
        delete params[k];
    });
    return params;
}

export function dateFormat(value) {
    dayjs.extend(relativeTime);
    return dayjs(`${value}`).fromNow();
}

export function debounce(callback, delay = 200) {
    let timeout;

    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            callback(...args);
        }, delay);
    };
}

export function throttle(callback, delay = 200) {
    let shouldWait = false;
    let waitingArgs;

    const timeoutFunc = () => {
        if (waitingArgs == null) {
            shouldWait = false;
        } else {
            callback(...waitingArgs);
            waitingArgs = null;
            setTimeout(timeoutFunc, delay);
        }
    };

    return (...args) => {
        if (shouldWait) {
            waitingArgs = args;
            return;
        }
        callback(...args);
        shouldWait = true;
        setTimeout(timeoutFunc, delay);
    };
}
