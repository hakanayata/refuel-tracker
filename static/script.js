setTimeout(() => {
    const flash_message = document.querySelector("header")

    flash_message.style.display = "none";
}, 5000);

function downloadPDF() {
    window.print();
}