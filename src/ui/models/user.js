import { BaseModel, Manager } from "./base";

class UserManager extends Manager {
  login(data) {
    const url = `${this.model.url}/login`;
    return this.doPost(url, data);
  }
  register(data) {
    const url = `${this.model.url}/register`;
    return this.doPost(url, data);
  }
}

export class User extends BaseModel {
  static endpoint = `/users`;

  static get objects() {
    return new UserManager(this);
  }
}
export default User;
