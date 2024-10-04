import state from "/store";
import User from "/models/user";

export function main() {
  return state;
}

export async function login(FormData, form) {
  // Using form.requestData will EXCLUDE conditional elements and it
  // will submit the form as "Content-Type: application/json".
  const data = form.requestData;

  // Show loading spinner
  form.submitting = state.loading;
  debugger
  User.objects.login(data).then((r) => {
    form.submitting = state.loading;
  });
}

export async function register(FormData, form) {
  const data = form.requestData;
  debugger;
  // Show loading spinner
  form.submitting = state.loading;

  User.objects.register(data).then((r) => {
    form.submitting = state.loading;
  });
}
