import { expect, test } from "vitest";
import Sample from "/models/sample";

test("main vue entry point", () => {
  const sample = Sample.objects.create({});
  expect(sample).toBeInstanceOf(Sample);
});
