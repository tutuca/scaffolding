import { expect, test, vi } from "vitest";
import Profile from "/models/profile";

global.fetch = vi.fn();

function createFetchResponse(data) {
  return { json: () => new Promise((resolve) => resolve(data)) };
}
test("main vue entry point", async () => {
  const PROFILE_RESPONSE = {
    user: 1,
    date_created: "2024-10-04T23:49:00-03:00",
    date_modified: "2024-10-04",
  };
  fetch.mockResolvedValue(createFetchResponse(PROFILE_RESPONSE));
  const profile = await Profile.objects.create({});
  expect(profile).toBeInstanceOf(Profile);
});
