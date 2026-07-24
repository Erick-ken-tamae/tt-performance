let pontosJogador = 0;
let pontosAdversario = 0;

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

