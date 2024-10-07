/*
A Queryset is a Collection of Models.
Has pagination information.
*/
export default class QuerySet extends Array {
    loading = false;
    page = null;
    nextPage = null;
    previousPage = null;
    count = null;
    current = null; // TODO: keep track of current with inner state.

    constructor(...args) {
        super(...args);
    }
    set page(value) {
        return Number.isNaN(value) ? 1 : value;
    }
    getByField(field, value) {
        return this.find((obj) => obj[field] == value);
    }
    getById(id) {
        return this.getByField("id", id);
    }
    next(current) {
        // XXX: should it make a fetch?
        const nextIndex = this.indexOf(current) + 1;
        return this[nextIndex];
    }
    previous(current) {
        // XXX: should it make a fetch?
        const previousIndex = this.indexOf(current) - 1;
        return this[previousIndex];
    }
}
