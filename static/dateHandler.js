window.onload = () => {

    // variables to be showed
    const datepicker_index_page = document.getElementById("index-datepicker")
    const timepicker_index_page = document.getElementById("index-timepicker")

    let current_date = new Date()
    // date part
    let current_year = current_date.getFullYear()
    let current_month = String(current_date.getMonth() + 1).padStart(2, '0');
    let current_day = String(current_date.getDate()).padStart(2, '0');
    // time part
    let current_hour = String(current_date.getHours()).padStart(2, '0');
    let current_min = String(current_date.getMinutes()).padStart(2, '0');
    datepicker_index_page.setAttribute('value', `${current_year}-${current_month}-${current_day}`);
    timepicker_index_page.setAttribute('value', `${current_hour}:${current_min}`);

    // variables to be sent to the DB
    const dateDB_index_page = document.getElementById("index-date")
    // date object instance
    d = new Date()
    dateDB_index_page.setAttribute('value', d.toISOString())

    datepicker_index_page.onchange = () => {
        dateDB = datepicker_index_page.value
        dateDB = dateDB.split("-")
        yearDB = Number(dateDB[0])
        monthDB = Number(dateDB[1]) - 1
        dayDB = Number(dateDB[2])
        d.setFullYear(yearDB)
        d.setMonth(monthDB)
        d.setDate(dayDB)
        dateDB_index_page.setAttribute('value', d.toISOString())
    }

    timepicker_index_page.onchange = () => {
        timeDB = timepicker_index_page.value
        timeDB = timeDB.split(":")
        hourDB = Number(timeDB[0])
        minDB = Number(timeDB[1])
        d.setHours(hourDB)
        d.setMinutes(minDB)
        d.setSeconds(0)
        d.setMilliseconds(0)
        dateDB_index_page.setAttribute('value', d.toISOString())
    }

}
