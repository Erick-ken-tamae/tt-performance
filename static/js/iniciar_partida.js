let pontosJogador = 0;
let pontosAdversario = 0;

let setsJogador = 0;
let setsAdversario = 0;

let encerrarPartida = false;

const setsParaVencer = Math.ceil(melhorDe / 2);

function atualizarPlacar(){

    document.getElementById("pontosJogador").innerText = pontosJogador;

    document.getElementById("pontosAdversario").innerText = pontosAdversario;
}

function atualizarSets(){

    document.getElementById("setsJogador").innerText = setsJogador;

    document.getElementById("setsAdversario").innerText = setsAdversario;
}

function marcarPonto(jogador, tipoMarcacao){

    if(encerrarPartida){
        return;
    }

    let nome;

    if(jogador === "jogador"){

        pontosJogador++;
        nome = nomeJogador;

    }else{

        pontosAdversario++;
        nome = nomeAdversario;
    }

    atualizarPlacar();

    adicionarHistoricoPonto(nome, tipoMarcacao);

    verificarVencedor();
}

function corrigirPonto(jogador){

    if(jogador === "jogador"){

        if(pontosJogador > 0){
            pontosJogador--;
        }

    }else{

        if(pontosAdversario > 0){
            pontosAdversario--;
        }
    }

    atualizarPlacar();
}

function registrarErro(jogador, tipoErro){

    if(encerrarPartida){
        return;
    }

    let nomeErro;
    let nomePonto;

    if(jogador === "jogador"){

        nomeErro = nomeJogador;
        nomePonto = nomeAdversario;

        pontosAdversario++;

    }else{

        nomeErro = nomeAdversario;
        nomePonto = nomeJogador;

        pontosJogador++;
    }

    atualizarPlacar();

    adicionarHistoricoErro(
        nomePonto,
        nomeErro,
        tipoErro
    );

    verificarVencedor();
}

function adicionarHistoricoPonto(nome, tipoMarcacao){

    let tipo = "";

    if(tipoMarcacao === "F"){
        tipo = "Forehand";
    }
    else if(tipoMarcacao === "B"){
        tipo = "Backhand";
    }
    else if(tipoMarcacao === "S"){
        tipo = "Saque";
    }

    const lista = document.getElementById("listaJogadas");

    if(!lista){
        return;
    }

    const jogada = document.createElement("div");

    jogada.classList.add("jogada");

    jogada.innerHTML = `
        <strong>🏓 Ponto para: ${nome}</strong><br>
        Tipo do ponto: ${tipo}
    `;

    lista.prepend(jogada);
}

function adicionarHistoricoErro(nomePonto, nomeErro, tipoErro){

    let tipo = "";

    if(tipoErro === "F"){
        tipo = "Forehand";
    }
    else if(tipoErro === "B"){
        tipo = "Backhand";
    }
    else if(tipoErro === "S"){
        tipo = "Saque";
    }

    const lista = document.getElementById("listaJogadas");

    if(!lista){
        return;
    }

    const jogada = document.createElement("div");

    jogada.classList.add("jogada");

    jogada.innerHTML = `
        <strong>🏓 Ponto para: ${nomePonto}</strong><br>
        ❌ Erro de: ${nomeErro}<br>
        Tipo do erro: ${tipo}
    `;

    lista.prepend(jogada);
}

function verificarVencedor(){

    if(
        pontosJogador >= 11 &&
        pontosJogador - pontosAdversario >= 2
    ){

        finalizarSet("jogador");
        return;
    }

    if(
        pontosAdversario >= 11 &&
        pontosAdversario - pontosJogador >= 2
    ){

        finalizarSet("adversario");
        return;
    }
}

function finalizarSet(vencedor){

    if(vencedor === "jogador"){

        setsJogador++;

    }else{

        setsAdversario++;
    }

    atualizarSets();

    if(setsJogador >= setsParaVencer){

        encerrarPartida = true;

        mostrarVitoria(nomeJogador);

        desabilitarBotoes();

        return;
    }

    if(setsAdversario >= setsParaVencer){

        encerrarPartida = true;

        mostrarVitoria(nomeAdversario);

        desabilitarBotoes();

        return;
    }

    pontosJogador = 0;
    pontosAdversario = 0;

    atualizarPlacar();

    alert("Fim do set! O próximo set vai começar.");
}

function desabilitarBotoes(){

    document.querySelectorAll(".btn-marcacao").forEach(function(botao){

        botao.disabled = true;

    });
}

function mostrarVitoria(vencedor){

    const popup = document.getElementById("popupVitoria");

    const mensagem = document.getElementById("mensagemVitoria");

    mensagem.innerHTML = `
        🏆
        <strong>${vencedor}</strong>
        venceu a partida!

        <br><br>

        Sets:
        <strong>${setsJogador} x ${setsAdversario}</strong>
    `;

    popup.style.display = "flex";
}

function fecharPopup(){

    document.getElementById("popupVitoria").style.display = "none";
}
