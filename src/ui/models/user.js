import { BaseModel, Manager } from "./base";

class UserManager extends Manager {
  login(data) {
    // TODO: add token based session.
    /*
    {
      "access": "access_token",
      "refresh": "refres_token",
      "user": {
        "pk": 1,
        "username": "admin",
        "email": "admin@admin.com",
        "first_name": "",
        "last_name": ""
      }
    }
    */
    const url = `${BaseModel.baseURL}/auth/login`;
    return this.doPost(url, data);
  }
  userByToken(token) {}
  register(data) {
    const url = `${BaseModel.baseURL}/register`;
    return this.doPost(url, data);
  }
}

export class User extends BaseModel {
  static endpoint = `/auth/user`;

  static get objects() {
    return new UserManager(this);
  }
}
export default User;
