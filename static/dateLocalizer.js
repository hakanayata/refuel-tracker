
window.addEventListener("DOMContentLoaded", () => {
    let dateCells = document.getElementsByClassName("dateNtime")

    if (dateCells) {
        for (let i = 0; i < dateCells.length; i++) {
            dateCells[i].innerHTML = new Date(`${dateCells[i].innerHTML}`).toLocaleString().slice(0, -3).replace(",", " |")
        }
    }
})
