



window.onload = () => {
    // variables to be showed (coming from DB)
    const datepicker_edit_page = document.getElementById("edit-datepicker")
    const timepicker_edit_page = document.getElementById("edit-timepicker")
    // complete date in GMT(Greenwich Median Time) format
    let dateCompleteGMT = new Date(`${datepicker_edit_page.value} ${timepicker_edit_page.value}:00+00:00`)
    // timezone offset is -60 for germany (in winter)
    let timezoneOffset = new Date().getTimezoneOffset()
    // local time
    let localDateTime = new Date(dateCompleteGMT - timezoneOffset)
    // date to show
    datepicker_edit_page.setAttribute('value', `${localDateTime.getFullYear()}-${localDateTime.getMonth() + 1}-${localDateTime.getDate()}`)
    timepicker_edit_page.setAttribute('value', localDateTime.toLocaleTimeString().slice(0, 5))

    // variables to be sent to the DB
    const dateDB_edit_page = document.getElementById("edit-date")
    // date object instance
    // d = new Date()
    d = new Date(`${dateDB_edit_page.value}`)

    datepicker_edit_page.onchange = () => {
        dateDB = datepicker_edit_page.value
        dateDB = dateDB.split("-")
        yearDB = Number(dateDB[0])
        monthDB = Number(dateDB[1]) - 1
        dayDB = Number(dateDB[2])
        d.setFullYear(yearDB)
        d.setMonth(monthDB)
        d.setDate(dayDB)
        dateDB_edit_page.setAttribute('value', d.toISOString())
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