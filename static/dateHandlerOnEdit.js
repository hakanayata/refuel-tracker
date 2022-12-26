
window.onload = () => {
    // variables to be showed (coming from DB)
    const datepicker_edit_page = document.getElementById("edit-datepicker")
    const timepicker_edit_page = document.getElementById("edit-timepicker")
    // complete date in GMT(Greenwich Median Time) format
    let dateCompleteGMT = new Date(`${datepicker_edit_page.value} ${timepicker_edit_page.value}:00+00:00`)

    // date to show
    // datepicker_edit_page.setAttribute('value', `${dateCompleteGMT.getFullYear()}-${dateCompleteGMT.getMonth() + 1}-${dateCompleteGMT.getDate()}`)
    datepicker_edit_page.setAttribute('value', `${('0' + String(dateCompleteGMT.getFullYear())).slice(-4)}-${('0' + (dateCompleteGMT.getMonth() + 1)).slice(-2)}-${('0' + String(dateCompleteGMT.getDate())).slice(-2)}`)
    timepicker_edit_page.setAttribute('value', `${('0' + String(dateCompleteGMT.getHours())).slice(-2)}:${('0' + String(dateCompleteGMT.getMinutes())).slice(-2)}`)

    // variables to be sent to the DB
    const dateDB_edit_page = document.getElementById("edit-date")
    // date object instance
    // d = new Date()
    d = new Date(`${dateDB_edit_page.value}`)

    datepicker_edit_page.onchange = () => {
        dateDB = datepicker_edit_page.value

        if (datepicker_edit_page.value != false) {
            dateDB = dateDB.split("-")
            yearDB = Number(dateDB[0])
            monthDB = Number(dateDB[1]) - 1
            dayDB = Number(dateDB[2])
            d.setDate(dayDB)
            d.setMonth(monthDB)
            d.setFullYear(yearDB)
            dateDB_edit_page.setAttribute('value', d.toISOString())
        }

    }

    timepicker_edit_page.onchange = () => {
        timeDB = timepicker_edit_page.value
        timeDB = timeDB.split(":")
        hourDB = Number(timeDB[0])
        minDB = Number(timeDB[1])
        d.setHours(hourDB)
        d.setMinutes(minDB)
        d.setSeconds(0)
        d.setMilliseconds(0)
        dateDB_edit_page.setAttribute('value', d.toISOString())
    }

}
