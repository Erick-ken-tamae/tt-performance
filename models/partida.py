from database import conectar

# Cadastrar partida
def cadastrar_partida(nome_jogador,
                      clube_jogador,
                      nome_adversario,
                      data_partida,
                      quantidade_sets):

    banco = conectar()
    cursor = banco.cursor()

    sql = """
    INSERT INTO partida
    (
        nome_jogador,
        clube_jogador,
        nome_adversario,
        quantidade_sets,
        data_partida
    )
    VALUES
    (%s,%s,%s,%s,%s)
    """

    valores = (
        nome_jogador,
        clube_jogador,
        nome_adversario,
        quantidade_sets,
        data_partida
    )

    cursor.execute(sql, valores)

    banco.commit()

    cursor.close()
    banco.close()


# Listar partidas
def listar_partida():

    banco = conectar()

    cursor = banco.cursor(dictionary=True)

    sql = """
    SELECT
        id,
        nome_jogador,
        clube_jogador,
        nome_adversario,
        quantidade_sets,
        sets_jogador,
        sets_adversario,
        status,
        data_partida
    FROM partida
    ORDER BY id DESC
    """

    cursor.execute(sql)

    partidas = cursor.fetchall()

    cursor.close()
    banco.close()

    return partidas


# Buscar uma partida
def buscar_partida(id):

    banco = conectar()

    cursor = banco.cursor(dictionary=True)

    sql = """
    SELECT *
    FROM partida
    WHERE id=%s
    """

    cursor.execute(sql, (id,))

    partida = cursor.fetchone()

    cursor.close()
    banco.close()

    return partida

def listar_historico():
    banco = conectar()
    cursor = banco.cursor(dictionary=True)
    
    sql = """
    SELECT *
    FROM partida
    WHERE status='Finalizada'
    ORDER BY id DESC
    """
    
    cursor.execute(sql)

    partidas = cursor.fetchall()

    cursor.close()
    banco.close()

    return partidas

def finalizar_partida(id, vencedor, sets_jogador, sets_adversario):

    banco = conectar()
    cursor = banco.cursor()

    sql = """
        UPDATE partida
        SET
            vencedor=%s,
            sets_jogador=%s,
            sets_adversario=%s,
            status='FINALIZADA'
        WHERE id=%s
    """

    cursor.execute(sql, (
        vencedor,
        sets_jogador,
        sets_adversario,
        id
    ))

    banco.commit()

    cursor.close()
    banco.close()