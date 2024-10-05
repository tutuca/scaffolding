import { expect, test, vi } from "vitest";
import { Sample } from "/models";

global.fetch = vi.fn();

function createFetchResponse(data) {
  return { json: () => new Promise((resolve) => resolve(data)) };
}

test("Create empty sample", async () => {
  const title = "sample title";
  const SAMPLE_RESPONSE = {
    id: 1,
    title: title,
  };
  fetch.mockResolvedValue(createFetchResponse(SAMPLE_RESPONSE));
  const sample = await Sample.objects.create({ title: title });
  expect(sample).toBeInstanceOf(Sample);
  expect(sample.id).toBe(1);
  expect(sample.route()).toBe("/samples/1");
});
