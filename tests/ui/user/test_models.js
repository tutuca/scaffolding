import { expect, test } from "vitest";
import User from "/models/user";

test("main vue entry point", () => {
  const user = User.objects.create({});
  expect(user).toBeInstanceOf(User);
});
