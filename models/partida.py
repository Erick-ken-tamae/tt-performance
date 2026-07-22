from database import conectar



# Cadastrar partida

def cadastrar_partida(jogador_id, adversario, data_partida):

    banco = conectar()

    cursor = banco.cursor()


    sql = """
        INSERT INTO partida
        (jogador_id, adversario, data_partida)
        VALUES (%s,%s,%s)
    """


    valores = (
        jogador_id,
        adversario,
        data_partida
    )


    cursor.execute(sql,valores)


    banco.commit()


    cursor.close()
    banco.close()





# Listar partidas

def listar_partida():

    banco = conectar()

    cursor = banco.cursor(dictionary=True)


    sql = """
    SELECT 
        partida.id,
        jogador.nome,
        partida.adversario,
        partida.data_partida

    FROM partida

    INNER JOIN jogador

    ON partida.jogador_id = jogador.id
    """


    cursor.execute(sql)


    partidas = cursor.fetchall()


    cursor.close()
    banco.close()


    return partidas