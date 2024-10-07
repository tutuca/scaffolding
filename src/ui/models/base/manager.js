import useStore from "/store";
import settings from "/models/conf";
import { cleanParams } from "/utils";
import QuerySet from "./queryset.js";
import Client from "./client.js";
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
    credentials: "same-origin",
    Accept: "application/json",
    ...Authorization(state),
});

export default class Manager {
    constructor(proto) {
        this.model = proto;
        this.url = proto.baseURL;
        this.state = useStore();
        this.client = new Client(this.state);
    }
    static get queryset() {
        return new QuerySet();
    }
    async one(objId) {
        const toFetch = `${this.model.url}/${objId}/`;
        const json = await this.client.doFetch(toFetch);
        return new this.model(json);
    }

    async many(query) {
        const cleanedParams = new URLSearchParams(cleanParams(query));
        const qs = new QuerySet();
        const url = `${this.model.url}/?${cleanedParams.toString()}`;
        const json = await this.client.doFetch(url);

        json.results.forEach((e) => qs.push(new this.model(e)));

        qs.count = json.count;
        qs.page = cleanedParams.page;
        qs.nextPage = json.next;
        qs.previousPage = json.previous;

        return qs;
    }

    async create(body, data) {
        const cleanedParams = cleanParams(data);
        const model = this.model;
        const json = await this.client.doPost(model.url, body, cleanedParams);
        const instance = new model(json);
        return instance;
    }

    async getOrCreate(id, body) {
        let instance;
        let maybe_created = id !== null;
        if (maybe_created) {
            try {
                // get it and update it
                instance = await this.one(id);
                instance.save({ ...body, id });
            } catch (e) {
                // or create it
                // TODO catch specific errors.
                instance = this.create({ ...body, id });
            }
        } else {
            // then create it
            instance = this.create({ ...body, id });
        }
        return instance;
    }
}
