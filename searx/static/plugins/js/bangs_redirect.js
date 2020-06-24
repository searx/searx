function setRedirectForBang() {
    let divOfRedirect = document.querySelector('.well')
    if(divOfRedirect) {
        console.log(divOfRedirect.children[0].innerHTML)
        window.location.href = divOfRedirect.children[0].innerHTML
    }
}

setRedirectForBang()