import store from "../store";
import settings from "../conf";
import { cleanParams } from "../utils";
// const BASE_URL = process.env.VUE_APP_BASE_URL;

const HEADERS = {
  "X-CSRFToken": settings.csrf(),
  "Content-Type": "application/json",
  "Accept": "application/json",
}


class QuerySet extends Array {
  loading = false;
  page = null;
  nextPage = null;
  previousPage = null;
  count = null;

  next() {
    const nextIndex = this.indexOf(store.current) + 1;
    return this[nextIndex];
  }

  previous() {
    const previousIndex = this.indexOf(store.current) - 1;
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
    store.loading = true;
    if (resp.status >= 400 && resp.status < 600) {
      throw resp;
    }
    const json = await resp.json();
    store.loading = false;
    return json;
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
    const json = await this.doFetch(toFetch, params);

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
      headers: HEADERS,
      credentials: "same-origin",
      ...params,
    };
    const toFetch = url;
    const json = await this.doFetch(toFetch, params);

    return json;
  }

  async one(objId, params) {
    params = params || {};
    store.loading = true;
    const toFetch = `${this.url}/${objId}/`;
    const json = await this.doFetch(toFetch, params);
    const instance = new this.model(json.data);
    store.loading = false;
    return instance;
  }

  async many(params) {
    params = params || {};
    const qs = new QuerySet();
    const json = await this.doFetch(this.url, params);
    const page = parseInt(params.page);

    json.results.forEach((e) => qs.push(new this.model(e)));

    qs.count = json.count;
    qs.page = Number.isNaN(page) ? 1 : page;
    qs.nextPage = json.next;
    qs.previousPage = json.previous;

    return qs;
  }
  async update(objId, body, params) {
    const url = `${this.baseURL}/${objId}`;
    const result = await this.objects.doPut(url, body, params);
    return result;
  }

  async create(body, params) {
    params = params || {};

    const json = await this.doPost(this.url, body, params);
    const instance = new this.model(json.data);
    return instance;
  }
}


export class BaseModel extends Object {
  static baseURL = settings.baseURL;

  constructor(data) {
    super();
    Object.assign(this, data);
  }

  static get objects() {
    return new Manager(this);
  }

  async save() {
    const body = cleanParams(this);
    const result = await this.objects.update(this.id, body);
    return result;
  }
}
