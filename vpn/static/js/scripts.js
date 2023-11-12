function toggleCheckbox(obj){
    obj.firstElementChild.classList.toggle('checked');
    let checkboxRememberMe = obj.getElementsByTagName('input')[0];
    checkboxRememberMe.checked = !checkboxRememberMe.checked;
}