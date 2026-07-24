let pontosJogador = 0;
let pontosAdversario = 0;
let encerrarPartida = false;

//placar dos jogadores
function adicionarPontoJogador(){
    if(encerrarPartida){
        return;
    }

    pontosJogador++;
    atualizarPlacar();
    verificarVencedor();
}

function adicionarPontoAdversario(){

    if(encerrarPartida){
        return;
    }
    
    pontosAdversario++;
    atualizarPlacar();
    verificarVencedor();
}

//Atualiza o placar
function atualizarPlacar(){
    document.getElementById("pontosJogador").innerHTML= pontosJogador;
    document.getElementById("pontosAdversario").innerHTML = pontosAdversario;
}

//Verifica o vencedor
function verificarVencedor(){

    if(pontosJogador < 11 && pontosAdversario < 11 ){
        return
    }

    //Diferença de pontos
    const diferenca = Math.abs(pontosJogador - pontosAdversario);

    //Para vencer precisa de 2 pontos de vantagem
    if(diferenca >=2){
        encerrarPartida = true;

        let vencedor;

        if(pontosJogador > pontosAdversario){
            vencedor = "Jogador"
        }else{
            vencedor ="Adversario"
        }
        alert(" PARBÉNS " + vencedor + " VENCEU A PARTIDA!!");
        //Desabilita os botões
        document.querySelectorAll("btn-ponto").forEach(function(botao){
            botao.disabled = true;
        });
    };
}


//registrando os pontos
function registrarPonto(){
    const ganhador = document.getElementById("ganhador").value;
    const tecnica = document.getElementById("tecnica").value;
    const erro = document.getElementById("erro").value;
    const observacao = document.getElementById("observacao").value;
    //aumentar placar
    if(ganhador ==="jogador"){
        pontosJogador++;
        document.getElementById("pontosJogador").innerText = pontosJogador;
    }else{
        pontosAdversario++;
        document.getElementById("pontosAdversario").innerText=pontosAdversario;
    }
    
    //HISTÓRICO DO PONTO
    const lista = document.getElementById("listaJogadas");
    const jogada = document.createElement("div");
    
    jogada.classList.add("jogada")
    jogada.innerHTML=`
        <strong>
        Ponto para:${ganhador}
        </strong>

        <br>
        
        Técnica: ${tecnica}
        
        <br>
        
        Erro: ${erro}
        
        <br>
        
        Observação: ${observacao}
        `;

        lista.prepend(jogada);
        //limpar a observação
        document.getElementById("observacao").value="";
}

