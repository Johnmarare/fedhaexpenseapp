const usernameField = document.querySelector("#usernameField");
const feedBackArea = document.querySelector(".invalid_feedback");
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput");
const emailField = document.querySelector("#emailField");
const emailFeedBackArea = document.querySelector(".emailFeedBackArea");
const submitBtn = document.querySelector(".submit-btn");
const passwordField = document.querySelector("#passwordField");
const showPasswordToggle = document.querySelector(".showPasswordToggle");

const handleToggleInput = (e) => {
  if (showPasswordToggle.textContent === "show") {
    showPasswordToggle.textContent = "hide";
    passwordField.setAttribute("type", "text")
  } else {
    showPasswordToggle.textContent = "show";
    passwordField.setAttribute("type", "password");
  }
};


showPasswordToggle.addEventListener("click", handleToggleInput);

// Function to check if the form can be submitted
const validateForm = () => {
  const usernameVal = usernameField.value.trim();
  const emailVal = emailField.value.trim();
  const passwordVal = passwordField.value.trim();

  if (!usernameVal || !emailVal || !passwordVal) {
    submitBtn.disabled = true;
    return;
  }
  // Enable submit btn if no field is invalid
  if (!usernameField.classList.contains('is-invalid') &&
    !emailField.classList.contains('is-invalid')) {
    submitBtn.disabled = false;
  } else {
    submitBtn.disabled = true;
  }
};
usernameField.addEventListener("keyup", (e) => {
  const usernameVal = e.target.value;

  usernameSuccessOutput.style.display = "block";

  usernameSuccessOutput.textContent = `Checking  ${usernameVal}`;

  usernameField.classList.remove("is-invalid");
  feedBackArea.style.display = "none";

  if (usernameVal.length > 0) {
    fetch("/authentication/validate-username", {
      body: JSON.stringify({ username: usernameVal }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        usernameSuccessOutput.style.display = "none";
        if (data.username_error) {
          usernameField.classList.add("is-invalid");
          feedBackArea.style.display = "block";
          feedBackArea.innerHTML = `<p>${data.username_error}</p>`;
          submitBtn.disabled = true;
        } else {
          submitBtn.removeAttribute("disabled");
        }
      });
  }
});

emailField.addEventListener("keyup", (e) => {
  const emailVal = e.target.value;

  emailField.classList.remove("is-invalid");
  emailFeedBackArea.style.display = "none";

  if (emailVal.length > 0) {
    fetch("/authentication/validate-email", {
      body: JSON.stringify({ email: emailVal }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("data", data);
        if (data.email_error) {
          submitBtn.disabled = true;
          emailField.classList.add("is-invalid");
          emailFeedBackArea.style.display = "block";
          emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
        } else {
          submitBtn.removeAttribute("disabled");
          emailFeedBackArea.style.display = "none";
        }
      });
  }
});

