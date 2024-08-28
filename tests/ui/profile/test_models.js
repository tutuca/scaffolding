import { expect, test } from "vitest";
import Profile from "/models/profile";

test("main vue entry point", () => {
  const profile = Profile.objects.create({});
  expect(profile).toBeInstanceOf(Profile);
});
