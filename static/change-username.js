const username = document.getElementById("username")
const confirmation = document.getElementById("confirmation")
const form = document.getElementById("form")
const errorDiv = document.getElementById("error")

document.addEventListener("DOMContentLoaded", () => {

    form.addEventListener('submit', (e) => {
        let errorMessages = []

        if (username.value === '' || username.value == null) {
            errorMessages.push("Must provide username!")
        }

        if (username.value !== confirmation.value) {
            errorMessages.push("Usernames do not match!")
        }

        if (errorMessages.length > 0) {
            e.preventDefault()
            errorDiv.innerText = errorMessages.join(', ')
        }

    })

})