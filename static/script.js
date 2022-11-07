setTimeout(() => {
    const flash_message = document.querySelector("header")

    flash_message.style.display = "none";
}, 4000);

function downloadPDF() {
    window.print();
}