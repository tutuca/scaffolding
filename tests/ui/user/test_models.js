import { expect, test, vi } from "vitest";
import User from "/models/user";

global.fetch = vi.fn();

function createFetchResponse(data) {
  return { json: () => new Promise((resolve) => resolve(data)) };
}

test("Create empty user", async () => {
  const USER_RESPONSE = {
    id: 1,
    username: "user",
  };
  fetch.mockResolvedValue(createFetchResponse(USER_RESPONSE));
  const user = await User.objects.create({ username: "user" });
  expect(user).toBeInstanceOf(User);
});

test("Login empty", async () => {
  const username = "user";
  const password = "secret";
  const last_login = new Date("12/12/13").toISOString();
  const date_joined = new Date("12/12/12").toISOString();
  const USER_RESPONSE = {
    access: "access_token",
    refresh: "refresh_token",
    user: {
      id: 1,
      username: username,
      email: "admin@admin.com",
      first_name: "",
      last_name: "",
      last_login: last_login,
      date_joined: date_joined,
    },
  };

  fetch.mockResolvedValue(createFetchResponse(USER_RESPONSE));
  const user = await User.objects.login({ username, password });
  expect(user).toBeInstanceOf(User);
  expect(user.id).toBe(1);
  expect(user.username).toBe(username);
  expect(user.access_token).toBe("access_token");
});
