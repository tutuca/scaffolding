export function randomChoice(arr) {
  return arr[Math.floor(arr.length * Math.random())];
}

export function cleanParams(params) {
  const keysForDel = [];
  for (const key in params) {
    if (Object.hasOwnProperty.call(params, key)) {
      const v = params[key];
      if (v === undefined || v === null || v === "") {
        keysForDel.push(key);
      }
    }
  }
  keysForDel.forEach((k) => {
    delete params[k];
  });
  return params;
}
