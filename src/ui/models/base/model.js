import { cleanParams } from "/utils";
import settings from "/models/conf";
import Manager from "./manager";

export default class BaseModel extends Object {
    static baseURL = settings.baseURL;
    static endpoint = "";
    constructor(data) {
        super();
        // TODO: add schema validation to `data`.
        // TODO: user class field for schema declaration.
        Object.assign(this, cleanParams(data));
    }
    get route() {
        return `${this.constructor.endpoint}/${this.id}`;
    }
    static get url() {
        return `${this.baseURL}${this.endpoint}`;
    }
    static get objects() {
        return new Manager(this);
    }

    async save(params) {
        const body = cleanParams(params);
        const cls = Object.getPrototypeOf(this).constructor;
        const url_called = cls.url + `/${params.id}`;
        const result = await cls.objects.doPatch(url_called, body, params);
        return result;
    }
    async delete(params) {
        const cls = Object.getPrototypeOf(this).constructor;
        const url = `${cls.url}/${this.id}`;
        return cls.objects.doDelete(url, params);
    }
}
