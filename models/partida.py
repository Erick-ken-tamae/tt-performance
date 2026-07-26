from database import conectar


def cadastrar_partida(nome, clube, adversario, data_partida):

    banco = conectar()
    cursor = banco.cursor()

    # Procurar o jogador pelo nome e clube
    sql_jogador = """
        SELECT id
        FROM jogador
        WHERE nome = %s
        AND clube = %s
    """

    cursor.execute(sql_jogador, (nome, clube))

    jogador = cursor.fetchone()

    # Se o jogador não existir, cadastrar
    if jogador is None:

        sql_cadastrar_jogador = """
            INSERT INTO jogador
            (nome, idade, clube)
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            sql_cadastrar_jogador,
            (nome, 19, clube)
        )

        jogador_id = cursor.lastrowid

    else:

        jogador_id = jogador[0]

    # Cadastrar a partida
    sql_partida = """
        INSERT INTO partida
        (jogador_id, adversario, data_partida)
        VALUES (%s, %s, %s)
    """

    cursor.execute(
        sql_partida,
        (jogador_id, adversario, data_partida)
    )

    banco.commit()

    cursor.close()
    banco.close()


def listar_partida():

    banco = conectar()

    cursor = banco.cursor(dictionary=True)

    sql = """
        SELECT
            p.id,
            j.nome,
            j.clube,
            p.adversario,
            p.data_partida

        FROM partida p

        INNER JOIN jogador j
            ON p.jogador_id = j.id

        ORDER BY p.id DESC
    """

    cursor.execute(sql)

    partidas = cursor.fetchall()

    cursor.close()
    banco.close()

    return partidas


def buscar_partida(id):

    banco = conectar()

    cursor = banco.cursor(dictionary=True)

    sql = """
        SELECT
            p.id,
            j.nome,
            j.clube,
            p.adversario,
            p.data_partida

        FROM partida p

        INNER JOIN jogador j
            ON p.jogador_id = j.id

        WHERE p.id = %s
    """

    cursor.execute(sql, (id,))

    partida = cursor.fetchone()

    cursor.close()
    banco.close()

    return partida