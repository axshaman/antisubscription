'use strict'

console.log('Connected to Script')

const mainFrom = document.querySelector('#request-form');

const loginInput = document.querySelector('#form_login');
const passwordInput = document.querySelector('#form_password');
// const emailServiceInput = document.querySelector('#form_email');

const dropDownButton = document.querySelector('#dropdownMenu2')
const yndexServiceChoice = document.getElementsByClassName('dropdown-item')[0];
const gmailServiceChoice = document.getElementsByClassName('dropdown-item')[1];
const mailruServiceChoice = document.getElementsByClassName('dropdown-item')[2];

const keyWordsInput = document.querySelector('#form_keywords');
// const resultTextArea = document.querySelector('#form_result');

let btnCheckMail = document.getElementsByClassName('btn btn-success btn-send')[0];
let btnShowResult = document.getElementsByClassName('btn btn-send')[1];


// ======   BLL   ======


dropDownButton.addEventListener('click', function(e) {
    yndexServiceChoice.addEventListener('click', function (e) {
        
        dropDownButton.innerHTML = 'Yandex'
        dropDownButton.value = 'imap.yandex.ru'
        console.log(dropDownButton.value);
    })
    gmailServiceChoice.addEventListener('click', function (e) {
        dropDownButton.innerHTML = 'Gmail'
        dropDownButton.value = 'imap.gmail.com'
        console.log(dropDownButton.value);
    })
    mailruServiceChoice.addEventListener('click', function (e) {
        dropDownButton.innerHTML = 'Mail.ru'
        dropDownButton.value = 'imap.mail.ru'
        console.log(dropDownButton.value);
    })
})





// FORM HANDLER
let mail_service, login, password, keyWords;

mainFrom.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!dropDownButton.value) {
        alert('Выберите Email Service');
    } else {
        onSubmit();
        console.log('onSubmit')
    }
    // console.log('CheckData')
})

function onSubmit(e) {
    // e.preventDefault();
    btnCheckMail.setAttribute('disabled', 'disabled')

    mail_service = dropDownButton.value
    // mail_service = 'imap.yandex.ru'

    login = loginInput.value
    password = passwordInput.value
    keyWords = keyWordsInput.value

    let request = {
        mail_service,
        login,
        password,
        keyWords
    }

    // console.log(request)


    fetch('http://monitoring.antipodpiska.ru/account', {

        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            mail_service,
            login,
            password,
            keyWords
        })
    }
    )
    .then((response) => {
        // console.log(response)
        btnShowResult.removeAttribute('disabled')
        btnCheckMail.removeAttribute('disabled')
    })
}

// Check data from DB
btnShowResult.addEventListener('click', function (e) {
    e.preventDefault();
    let login = loginInput.value;
    if (login.length < 1) {
        alert('Введите Login имэйла');
    } else {
        getDataWithFetch();
    }
    // console.log('CheckData')
})


// Getting DATA from DB
let getDataWithFetch = () => {
    let login = loginInput.value;
   
    
    fetch('http://monitoring.antipodpiska.ru/senders?login=' + login)
        .then((response) => {
            // console.log(typeof response)
            // console.log(response)
            return response.json();
        })
      
        .then((data) => {
            // debugger;
            let data1 = data[0]
            let data2 = data[1]
            let count_data = data1.length
            if (count_data = 1) {
                // console.log(data[0]['Send Date'])
                let date_str = data1[0]['Send Date'].substring(0, 16)
            } else {
                // console.log(data[3]['Send Date'])
                let date_str = data1[3]['Send Date'].substring(0, 16)
            }
            
           
            if (data1.length > 0 || data2.length > 0) {
                // debugger;
                let temp = '';
                let id = data1.length

                {data1.forEach((itemData) => {
                    // debugger;
                    if (loginInput.value == itemData['Recipient']) {
                        temp += "<tr>";
                        temp += "<td>" + id + "</td>"
                        temp += "<td>" + itemData['Send Date'].substring(0, 16) + "</td>"
                        temp += "<td>" + itemData['sender'] + "</td>"
                        temp += "<td>" + itemData['Subscription'] + "</td></tr>";
                        --id;
                        document.getElementById('data').innerHTML = temp;
                    }
                });
            }
                let temp2 = '';
                let id2 = data2.length
                data2.forEach((itemData2) => {
                    // debugger;
                    // if (loginInput.value == itemData['Recipient']) {
                        temp2 += "<tr>";
                        temp2 += "<td>" + id2 + "</td>"
                        temp2 += "<td>" + itemData2['Last Send Date'].substring(0, 16) + "</td>"
                        temp2 += "<td>" + itemData2['Sender of Subscription'] + "</td>"
                        temp2 += "<td>" + itemData2['Periods'] + "</td></tr>";
                        console.log(itemData2['Last Send Date'])
                        --id2;
                        document.getElementById('periods').innerHTML = temp2;
                    // }
                });
        }

        })
}


