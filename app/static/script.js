function setCookie(cname, cvalue, exdays) {
  let d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  let expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  let name = cname + "=";
  let ca = document.cookie.split(';');
  for(let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

const mailinglist = document.getElementById("prompt");

function showMailingList() {
  mailinglist.style.bottom = "20px";
}

function hideMailingList() {
  mailinglist.style.bottom = "-200px";
  setCookie("closed", "yes", 2);
}

function signedUp() {
  setCookie("closed", "yes", 1000000);
}

function checkOnLoad() {
  if (getCookie("closed") == "") {
    setTimeout(() => {
      showMailingList();
    }, 5000);
  }
}
