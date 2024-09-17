import state from "/store";
import settings from "/models/conf";
import { cleanParams } from "/utils";
import QuerySet from "./queryset.js";

const HEADERS = {
  "X-CSRFToken": settings.csrf,
  "Content-Type": "application/json",
  Accept: "application/json",
};

export default class Manager {
  constructor(proto) {
    this.model = proto;
    this.url = proto.baseURL;
  }
  static get queryset() {
    return new QuerySet();
  }
  async doFetch(url, params) {
    // TODO: buy some coupling with vue and use composables
    // https://vuejs.org/guide/reusability/composables#async-state-example
    const resp = await fetch(url, params);
    state.loading = true;
    if (resp.status >= 400 && resp.status < 600) {
      throw resp;
    }
    const json = await resp.json();
    state.loading = false;
    return json;
  }

  async doPatch(url, body, params) {
    // generalize headers and credentials in this and doPost
    body = JSON.stringify(cleanParams(body));

    params = {
      method: "PATCH",
      body: body,
      headers: HEADERS,
      credentials: "same-origin",
      ...params,
    };
    const toFetch = url;
    const json = await this.doFetch(toFetch, params);

    return json;
  }
  async doDelete(url, params) {
    params = {
      method: "DELETE",
      headers: HEADERS,
      credentials: "same-origin",
      ...params,
    };

    return fetch(url, params);
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
    return this.doFetch(url, params);
  }

  async one(objId) {
    const toFetch = `${this.model.url}/${objId}/`;
    const json = await this.doFetch(toFetch);
    return new this.model(json);
  }

  async many(query) {
    const cleanedParams = new URLSearchParams(cleanParams(query));
    const qs = new QuerySet();
    const url = `${this.model.url}/?${cleanedParams.toString()}`;
    const json = await this.doFetch(url);

    json.forEach((e) => qs.push(new this.model(e)));

    qs.count = json.count;
    qs.page = cleanedParams.page;
    qs.nextPage = json.next;
    qs.previousPage = json.previous;

    return qs;
  }

  async create(body, data) {
    const cleanedParams = cleanParams(data);
    const model = this.model;
    const json = await this.doPost(model.url, body, cleanedParams);
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
