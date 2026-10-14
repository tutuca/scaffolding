// A place in a tree, named by labels, so it can be found again in a tree that was
// rebuilt: the telescope's zoom has to survive the page being swapped for a new one.
// Browser-free.

/** The nodes from `root` down the labels, stopping where a label is no longer a child. */
export function walk(root, labels) {
  const nodes = [root];
  for (const label of labels) {
    const child = nodes.at(-1).children.find((node) => node.label === label);
    if (!child) break;
    nodes.push(child);
  }
  return nodes;
}

/** The labels below the root: what `walk` takes. */
export const named = (nodes) => nodes.slice(1).map((node) => node.label);
