// The form's script: it sprinkles upon the markup Django rendered and builds none.
//
// The browser already validates a form from the attributes Django's widgets emit (`required`,
// `maxlength`, `min`, `step`, `type`). What this adds is where the message appears: not in
// the browser's bubble, which covers the field and goes in a moment, but in the field's own
// `[data-live]` slot - the empty error list `form_field.html` draws after the server's - while the
// reader types, and for every invalid field at once when they try to send. The server's
// errors stay where Django put them; a field the reader is fixing loses its mark as soon as
// it is valid, and there is nothing here that is not read off `validity`.
const slotOf = (control) => control.closest("div")?.querySelector("[data-live]");

function show(control) {
  const slot = slotOf(control);
  if (!slot) return;
  const invalid = !control.validity.valid;
  slot.hidden = !invalid;
  slot.firstElementChild.textContent = invalid ? control.validationMessage : "";
  if (invalid) control.setAttribute("aria-invalid", "true");
  else control.removeAttribute("aria-invalid");
}

// A field is judged once the reader has been in it; after that, on every keystroke.
const touched = new WeakSet();
document.addEventListener("focusout", (event) => {
  if (!slotOf(event.target)) return;
  touched.add(event.target);
  show(event.target);
});
document.addEventListener("input", (event) => {
  if (touched.has(event.target)) show(event.target);
});

// Sending an invalid form: every message at once, in place, and the cursor in the first
// field that needs it - what the browser's bubble would have done, one field at a time.
let focusing = false;
document.addEventListener(
  "invalid",
  (event) => {
    if (!slotOf(event.target)) return;
    event.preventDefault();
    touched.add(event.target);
    show(event.target);
    if (focusing) return;
    focusing = true;
    queueMicrotask(() => {
      focusing = false;
      event.target.form?.querySelector(":invalid")?.focus();
    });
  },
  true,
);
