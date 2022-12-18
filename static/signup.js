const username = document.getElementById("username")
const password = document.getElementById("password")
const form = document.getElementById("form")
const errorDiv = document.getElementById("error")

document.addEventListener("DOMContentLoaded", () => {

    console.log('i work')

    form.addEventListener('submit', (e) => {
        let errorMessages = []
        const pattern = "^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*_=+-.]).{8,20}$"

        if (username.value === '' || username.value == null) {
            errorMessages.push("Must provide username!")
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
        }

        if (errorMessages.length > 0) {
            e.preventDefault()
            errorDiv.innerText = errorMessages.join(', ')
        }

    })

})

