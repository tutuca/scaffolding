import state from "/store";
import User from "/models/user";
import { onBeforeMount } from "vue";

export function main() {
  onBeforeMount(() => {
    User.objects.many().then((response) => {
      state.queryset = response;
    });
  });
  return state;
}

export async function login(form, FormData) {
  // Using form.requestData will EXCLUDE conditional elements and it
  // will submit the form as "Content-Type: application/json".
  const data = form.requestData;

  // Show loading spinner
  form.submitting = state.loading;

  User.objects.login(data).then((r) => {
    form.submitting = state.loading;
  });

  // Handle success (status is 2XX)
  console.log("success", response);
}

export async function register(form, FormData) {
  const data = form.requestData;
  debugger;
  // Show loading spinner
  form.submitting = state.loading;

  User.objects.register(data).then((r) => {
    form.submitting = state.loading;
  });
}
