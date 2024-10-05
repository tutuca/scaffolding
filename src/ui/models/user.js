import { BaseModel, Manager } from "./base";
import dayjs from "dayjs";

class UserManager extends Manager {
  login(data) {
    // TODO: add token based session.

    const url = `${BaseModel.baseURL}/auth/login`;
    const user = this.doPost(url, data).then((data) => {
      return new this.model(data);
    });
    return user;
  }
  getSession(user) {}
  register(data) {
    const url = `${BaseModel.baseURL}/register`;
    return this.doPost(url, data);
  }
}

export class User extends BaseModel {
  static endpoint = `/auth/user`;

  constructor(data) {
    /* example API Response
        {
          "access": "access_token",
          "refresh": "refres_token",
          "user": {
            "pk": 1,
            "username": "admin",
            "email": "admin@admin.com",
            "first_name": "",
            "last_name": "",
            "last_login": "",
            "date_joined": "",
          }
        }
        */
    const user_data = data.user;
    user_data.access_token = data.access;
    user_data.refresh_token = data.refresh;

    user_data.date_joined = user_data.date_joined
      ? dayjs(user_data.date_joined)
      : null;
    user_data.last_login = user_data.last_login
      ? dayjs(user_data.last_login)
      : null;
    super(user_data);
  }
  static get objects() {
    return new UserManager(this);
  }
  static get session() {
    this.objects.getSession(this);
  }
}
export default User;
