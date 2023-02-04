const old_password = document.getElementById("old-password")
const password = document.getElementById("password")
const confirmation = document.getElementById("confirmation")
const form = document.getElementById("form")
const errorDiv = document.getElementById("error")

document.addEventListener("DOMContentLoaded", () => {

    form.addEventListener('submit', (e) => {
        let errorMessages = []
        const pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*_=+-.]).{8,20}$"

        if (old_password.value === '' || old_password.value == null) {
            errorMessages.push("Must provide old password!")
        }

        if (password.value === '' || password.value == null) {
            errorMessages.push("Must provide password!")
        }


        if (password.value.length < 8) {
            errorMessages.push("Password must contain at least 8 characters!")
        }

        if (password.value.length > 20) {
            errorMessages.push("Password can not be longer than 20 characters!")
        }

        if (password.value.length >= 8 && password.value.length <= 20) {
            if (password.value.match(pattern) == '' || password.value.match(pattern) == null) {
                errorMessages.push("Password must contain at least one lowercase, one uppercase letter, one number, and one special character! ('!', '@', '#', '$', '%', '^', '&', '*', '_', '=', '+', '-', '.')")
            }
            if (password.value !== confirmation.value) {
                errorMessages.push("Passwords do not match!")
            }
        }

        if (errorMessages.length > 0) {
            e.preventDefault()
            errorDiv.innerText = errorMessages.join(', ')
        }

    })

})