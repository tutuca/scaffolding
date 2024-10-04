import state from "/store";
import router from "/router";
import User from "/models/user";

export function main() {
  return state;
}

function loginError(error) {
  return error;
}
function loginSuccess(response) {
  state.session = {
    token: response.token,
    username: response.username,
    user_id: response.id,
  };
  return router.push("/profile");
}

export async function login(form, formData) {
  const data = form.data;

  // Show loading spinner
  form.submitting = true;
  let response;

  try {
    response = await User.objects.login(data);
  } catch (error) {
    return loginError(error);
  } finally {
    form.submitting = false;
  }

  if (response) {
    loginSuccess(response);
  }
  return state;
}

export async function register(form) {
  const data = form.requestData;
  // Show loading spinner
  form.submitting = state.loading;

  User.objects.register(data).then((r) => {
    form.submitting = state.loading;
  });
}
