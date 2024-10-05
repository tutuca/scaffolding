import state from "/store";
import router from "/router";
import User from "/models/user";

export function main() {
  return state;
}

function loginError(error) {
  console.log(error);

  return error;
}
function loginSuccess(user) {
  state.session = {
    token: user.access_token,
    user: user,
  };
  debugger;
  return router.push({ name: "profileDetail", params: { id: user.id } });
}

export async function login(form, formData) {
  const data = form.data;

  // Show loading spinner
  form.submitting = true;
  let user;

  try {
    user = await User.objects.login(data);
  } catch (error) {
    return loginError(error);
  } finally {
    form.submitting = false;
  }

  if (user) {
    loginSuccess(user);
  }
  return state;
}

export async function logout(form, formData) {
  const data = form.data;

  // Show loading spinner
  form.submitting = true;
  let user;

  try {
    user = await User.objects.logout(data);
  } catch (error) {
    return loginError(error);
  } finally {
    form.submitting = false;
  }

  if (user) {
    loginSuccess(user);
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
