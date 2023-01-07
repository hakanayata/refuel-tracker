window.addEventListener("DOMContentLoaded", () => {
    let dateCells = document.getElementsByClassName("dateNtime")

    if (dateCells) {
        for (let i = 0; i < dateCells.length; i++) {
            dateCells[i].innerHTML = new Date(`${dateCells[i].innerHTML}`).toLocaleString().slice(0, -3).replace(",", " |")
        }
    }

    // Show table data after script is done with everything.
    if (document.getElementById("table-show-onload")) {
        document.getElementById("table-show-onload").style.visibility = "visible";
    }

    if (document.getElementById("table-to-print")) {
        document.getElementById("table-to-print").style.visibility = "visible";
    }
})


