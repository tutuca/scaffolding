import state from "../store";
import settings from "../conf";
import { cleanParams } from "../utils";

export class QuerySet extends Array {
  loading = false;
  page = null;
  nextPage = null;
  previousPage = null;
  count = null;

  next() {
    const nextIndex = this.indexOf(state.current) + 1;
    return this[nextIndex];
  }

  previous() {
    const previousIndex = this.indexOf(state.current) - 1;
    return this[previousIndex];
  }
}

export class Manager {
  constructor(proto) {
    this.model = proto;
    this.url = proto.baseURL;
  }
  async doFetch(url, params) {
    const resp = await fetch(url, params);
    state.loading = true;
    if (resp.status >= 400 && resp.status < 600) {
      throw resp;
    }
    const json = await resp.json();
    state.loading = false;
    return json;
  }

  async doPost(url, body, params) {
    body = JSON.stringify(cleanParams(body));

    if (!url.endsWith("/")) {
      url = url + "/";
    }

    params = {
      method: "POST",
      body: body,
      headers: {
        "X-CSRFToken": settings.csrf(),
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      credentials: "same-origin",
      ...params,
    };
    return this.doFetch(url, params);
  }

  async doPut(url, body, params) {
    // generalize headers and credentials in this and doPost
    body = JSON.stringify(cleanParams(body));

    params = {
      method: "PUT",
      body: body,
      headers: HEADERS,
      credentials: "same-origin",
      ...params,
    };
    const toFetch = url;
    return this.doFetch(toFetch, params);
  }

  async one(objId) {
    const toFetch = `${this.model.url}/${objId}/`;
    const json = await this.doFetch(toFetch);
    return new this.model(json);
  }

  async many(params) {
    params = new URLSearchParams(params) || {};
    const qs = new QuerySet();
    const json = await this.doFetch(`${this.model.url}/?${params.toString()}`);
    const page = parseInt(params.page);
    json.results.forEach((e) => qs.push(new this.model(e)));

    qs.count = json.count;
    qs.page = Number.isNaN(page) ? 1 : page;
    qs.nextPage = json.next;
    qs.previousPage = json.previous;

    return qs;
  }

  async create(body, params) {
    params = params || {};
    const model = this.model;
    const json = await this.doPost(model.url, body, params);
    const instance = new model(json);
    return instance;
  }
}

export default class BaseModel extends Object {
  static baseURL = settings.baseURL;

  constructor(data) {
    super();
    Object.assign(this, data);
  }
  static get url() {
    return `${this.baseURL}${this.endpoint}`;
  }
  static get objects() {
    return new Manager(this);
  }

  async save(params) {
    const body = cleanParams(this);
    const cls = Object.getPrototypeOf(this).constructor;
    const result = await cls.objects.doPost(this.url, body, params);
    return result;
  }
}
