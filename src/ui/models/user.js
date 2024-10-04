import { BaseModel, Manager } from "./base";

class UserManager extends Manager {
  login(data) {
    const url = `${BaseModel.baseURL}/login`;
    return this.doPost(url, data);
  }
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
