document.addEventListener("DOMContentLoaded", () => {

    // flash message time limit
    if (document.body.contains(document.querySelector("header"))) {
        setTimeout(() => {

            const flash_message = document.querySelector("header")
            flash_message.style.display = "none";

        }, 5000);
    }
})

// save pdf on history page
// function downloadPDF() {
//     window.print();
// }