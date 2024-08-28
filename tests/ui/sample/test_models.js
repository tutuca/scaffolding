import { expect, test, vi } from "vitest";
import { Sample } from "/models";

global.fetch = vi.fn();

function createFetchResponse(data) {
  return { json: () => new Promise((resolve) => resolve(data)) };
}

test("Create empty sample", async () => {
  const SAMPLE_RESPONSE = {
    id: 1,
    title: "sample-title",
  };
  fetch.mockResolvedValue(createFetchResponse());
  const sample = await Sample.objects.create(SAMPLE_RESPONSE);
  expect(sample).toBeInstanceOf(Sample);
});
