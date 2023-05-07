//      Навигация       //

const navLinks = document.querySelectorAll('.nav_link')

navLinks.forEach(item => {
    item.addEventListener('mouseover', showAccordion)
    item.addEventListener('mouseout', hideAccordion)
})

function showAccordion() {
    const accordion = this.querySelector('.accordion')
    if (accordion) {
        accordion.style.display = 'block'
    }

}

function hideAccordion() {
    const accordion = this.querySelector('.accordion')
    if (accordion) {
        accordion.style.display = 'none'
    }
}

//      Конец навигации     //

//      Выпадающее меню месяцев     //

const month = document.querySelector('.month')
const monthList = document.querySelector('.month_list')

if (month) {
    month.addEventListener('click', toggleMonthMenu)
}

function toggleMonthMenu() {
    if (monthList.style.display == 'none') {
        monthList.style.display = 'flex'
    } else {
        monthList.style.display = 'none'
    }
}

document.addEventListener('click', function (e) {
    if (!e.target.closest('.month') && month) {
        monthList.style.display = 'none'
    }
})

//      Конец выпадающее меню месяцев       //

//      Мобильная навигация     //

const burger = document.querySelector('.burger')
const nav = document.querySelector('nav')

burger.addEventListener('click', toggleMobileMenu)

document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav_link') && window.innerWidth < 990) {
        nav.style.display = 'none'
    }
})

function toggleMobileMenu(e) {
    e.stopPropagation()
    if (nav.style.display === 'flex') {
        nav.style.display = 'none'
    } else {
        nav.style.display = 'flex'
    }
}

//      Конец мобильная навигация       //
