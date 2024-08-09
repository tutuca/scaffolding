import { BaseModel, Manager } from "./base";

export class Sample extends BaseModel {
  static baseURL = `${BaseModel.baseURL}/samples`;

  constructor(data) {
    super(data);
  }
}
export default Sample;
