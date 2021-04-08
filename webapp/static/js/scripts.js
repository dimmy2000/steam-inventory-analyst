//функция для перехода по ссылке
function openUrl(link) {
    location.href = link;
}
//получить путь к текущей странице
document.getElementById("sampleId").innerHTML = window.location.pathname;
