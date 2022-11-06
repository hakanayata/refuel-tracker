setTimeout(() => {
    const flash_message = document.querySelector("header")

    flash_message.style.display = "none";
}, 3500);

function downloadPDF() {
    window.print();
}