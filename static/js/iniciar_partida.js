console.log("JS DA PARTIDA CARREGADO");

let pontosJogador=0;
let pontosAdversario=0;
let setsJogador=0;
let setsAdversario=0;
let numeroSetAtual=1;
let encerrarPartida=false;

const setsParaVencer=Math.ceil(melhorDe/2);

function atualizarPlacar(){
    document.getElementById("pontosJogador").innerText=pontosJogador;
    document.getElementById("pontosAdversario").innerText=pontosAdversario;
}

function atualizarSets(){
    document.getElementById("setsJogador").innerText=setsJogador;
    document.getElementById("setsAdversario").innerText=setsAdversario;
}

function marcarPonto(jogador,tipo){
    if(encerrarPartida)return;

    let nome;

    if(jogador==="jogador"){
        pontosJogador++;
        nome=nomeJogador;
    }else{
        pontosAdversario++;
        nome=nomeAdversario;
    }

    atualizarPlacar();
    adicionarHistoricoPonto(nome,tipo);
    verificarVencedor();
}

function corrigirPonto(jogador){
    if(jogador==="jogador"){
        if(pontosJogador>0)pontosJogador--;
    }else{
        if(pontosAdversario>0)pontosAdversario--;
    }

    atualizarPlacar();
}

function registrarErro(jogador,tipo){

    if(encerrarPartida)return;

    let erro;
    let ponto;

    if(jogador==="jogador"){
        erro=nomeJogador;
        ponto=nomeAdversario;
        pontosAdversario++;
    }else{
        erro=nomeAdversario;
        ponto=nomeJogador;
        pontosJogador++;
    }

    atualizarPlacar();
    adicionarHistoricoErro(ponto,erro,tipo);
    verificarVencedor();
}

function verificarVencedor(){

    if(pontosJogador>=11 && pontosJogador-pontosAdversario>=2){
        finalizarSet("jogador");
        return;
    }

    if(pontosAdversario>=11 && pontosAdversario-pontosJogador>=2){
        finalizarSet("adversario");
    }
}

function finalizarSet(vencedor){

    salvarSetBanco(vencedor);

    if(vencedor==="jogador"){
        setsJogador++;
    }else{
        setsAdversario++;
    }

    atualizarSets();

    if(setsJogador>=setsParaVencer){
        encerrarPartida=true;
        salvarResultado(nomeJogador);
        mostrarVitoria(nomeJogador);
        desabilitarBotoes();
        return;
    }

    if(setsAdversario>=setsParaVencer){
        encerrarPartida=true;
        salvarResultado(nomeAdversario);
        mostrarVitoria(nomeAdversario);
        desabilitarBotoes();
        return;
    }

    numeroSetAtual++;

    pontosJogador=0;
    pontosAdversario=0;

    atualizarPlacar();

    alert("Fim do set!");
}

function salvarSetBanco(vencedor){

    let nomeVencedor;

    if(vencedor==="jogador"){
        nomeVencedor=nomeJogador;
    }else{
        nomeVencedor=nomeAdversario;
    }

    let dados={
        partida_id:partidaId,
        numero_set:numeroSetAtual,
        pontos_jogador:pontosJogador,
        pontos_adversario:pontosAdversario,
        vencedor:nomeVencedor
    };

    console.log("Enviando set:",dados);

    fetch("/salvar_set",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify(dados)
    })
    .then(res=>res.json())
    .then(data=>{
        console.log(data);
    })
    .catch(erro=>{
        console.log(erro);
    });
}

function salvarResultado(vencedor){

    fetch("/finalizar_partida",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            partida_id:partidaId,
            vencedor:vencedor,
            sets_jogador:setsJogador,
            sets_adversario:setsAdversario
        })
    });
}

function desabilitarBotoes(){
    document.querySelectorAll(".btn-marcacao")
    .forEach(botao=>{
        botao.disabled=true;
    });
}

function mostrarVitoria(vencedor){

    const popup=document.getElementById("popupVitoria");
    const mensagem=document.getElementById("mensagemVitoria");

    mensagem.innerHTML=`
    🏆 <strong>${vencedor}</strong> venceu!
    <br><br>
    Sets: ${setsJogador} x ${setsAdversario}
    `;

    popup.style.display="flex";

    document.getElementById("btnHistorico").style.display="inline-block";
}

function fecharPopup(){
    window.location.href="/historico/"+partidaId;
}

function adicionarHistoricoPonto(nome,tipo){

    let tecnica={
        F:"Forehand",
        B:"Backhand",
        S:"Saque"
    }[tipo];

    let lista=document.getElementById("listaJogadas");

    if(!lista)return;

    let div=document.createElement("div");

    div.classList.add("jogada");

    div.innerHTML=`
    🏓 Ponto para ${nome}<br>
    Técnica: ${tecnica}
    `;

    lista.prepend(div);
}

function adicionarHistoricoErro(ponto,erro,tipo){

    let tecnica={
        F:"Forehand",
        B:"Backhand",
        S:"Saque"
    }[tipo];

    let lista=document.getElementById("listaJogadas");

    if(!lista)return;

    let div=document.createElement("div");

    div.classList.add("jogada");

    div.innerHTML=`
    🏓 Ponto para ${ponto}<br>
    ❌ Erro de ${erro}<br>
    Técnica: ${tecnica}
    `;

    lista.prepend(div);
}