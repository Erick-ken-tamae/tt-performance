function abrirPopup(){
    document.getElementById("popupPartida").style.display = "flex";
}

function fecharPopup(){
    document.getElementById("popupPartida").style.display = "none";
}

// Remove a notificação (toast) do DOM depois que a animação termina
document.addEventListener("DOMContentLoaded", function () {
    const toast = document.getElementById("toastNotificacao");
    if (toast) {
        setTimeout(() => toast.remove(), 3500);
    }
});