import { BaseModel, Manager } from "./base";
import dayjs from "dayjs";

class UserManager extends Manager {
    serializeLogin(data) {
        const userData = data.user;
        userData.access_token = data.access;
        userData.refresh_token = data.refresh;

        userData.date_joined = userData.date_joined
            ? dayjs(userData.date_joined)
            : null;
        userData.last_login = userData.last_login
            ? dayjs(userData.last_login)
            : null;
        return userData;
    }
    login(data) {
        // TODO: add token based session.

        const url = `${BaseModel.baseURL}/auth/login`;
        const user = this.client.doPost(url, data).then((data) => {
            const userData = this.serializeLogin(data);
            return new this.model(userData);
        });
        return user;
    }
    getSession(user) {}
    register(data) {
        const url = `${BaseModel.baseURL}/register`;
        return this.client.doPost(url, data);
    }
}

export class User extends BaseModel {
    static endpoint = `/auth/user`;

    static get objects() {
        return new UserManager(this);
    }
    static get session() {
        this.objects.getSession(this);
    }
}
export default User;
