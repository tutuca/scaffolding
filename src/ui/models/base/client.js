import settings from "/models/conf";
import { cleanParams } from "/utils";

const Authorization = (state) => {
    let header = {};
    if (state.session && state.session.token) {
        header["Authorization"] = `bearer ${
            state.session ? state.session.token : null
        }`;
    }
    return header;
};

const buildHeaders = (state) => ({
    "X-CSRFToken": settings.csrf,
    "Content-Type": "application/json",
    // credentials: "same-origin",
    Accept: "application/json",
    ...Authorization(state),
});

class HTTPClient {
    constructor(state) {
        this.state = state;
    }
    async doFetch(url, params) {
        // TODO: buy some coupling with vue and use composables
        // https://vuejs.org/guide/reusability/composables#async-state-example
        const headers = buildHeaders(this.state);
        const resp = await fetch(url, {
            headers,
            ...params,
        });

        this.state.loading = true;
        if (resp.status >= 400 && resp.status < 600) {
            throw resp;
        }
        const json = await resp.json();
        this.state.loading = false;
        return json;
    }

    async doPatch(url, body, params) {
        // generalize headers and credentials in this and doPost
        body = JSON.stringify(cleanParams(body));

        const toFetch = url;
        const json = await this.doFetch(toFetch, {
            method: "PATCH",
            body: body,
            ...params,
        });

        return json;
    }
    async doDelete(url, params) {
        return await doFetch(url, {
            method: "DELETE",
            ...params,
        });
    }
    async doPost(url, body, params) {
        body = JSON.stringify(cleanParams(body));

        if (!url.endsWith("/")) {
            url = url + "/";
        }

        return this.doFetch(url, {
            method: "POST",
            body: body,
            ...params,
        });
    }
}

export default HTTPClient;
