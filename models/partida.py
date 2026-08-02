from database import conectar

# Cadastrar partida
def cadastrar_partida(nome_jogador,
                      clube_jogador,
                      nome_adversario,
                      clube_adversario,
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
        clube_adversario,
        quantidade_sets,
        data_partida
    )
    VALUES
    (%s,%s,%s,%s,%s,%s)
    """

    valores = (
        nome_jogador,
        clube_jogador,
        nome_adversario,
        clube_adversario,
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
            clube_adversario,
            quantidade_sets,
            sets_jogador,
            sets_adversario,
            status,
            data_partida
        FROM partida
        ORDER BY id ASC
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

def excluir_partida(id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM jogada
        WHERE partida_id=%s
    """,(id,))

    cursor.execute("""
        DELETE FROM partida
        WHERE id=%s
    """,(id,))

    conexao.commit()

    cursor.close()
    conexao.close()
    
def salvar_jogada(partida_id,set_numero,jogador, vencedor_ponto,tecnica,resultado):

    banco=conectar()
    cursor=banco.cursor()

    sql="""
    INSERT INTO jogada
    (
        partida_id,
        numero_set,
        jogador,
        vencedor_ponto,
        tecnica,
        resultado
    )
    VALUES
    (%s,%s,%s,%s,%s, %s)
    """

    cursor.execute(sql,(
        partida_id,
        set_numero,
        jogador,
        vencedor_ponto,
        tecnica,
        resultado
    ))

    banco.commit()

    cursor.close()
    banco.close()

def listar_sets(partida_id):

    banco = conectar()

    cursor = banco.cursor(dictionary=True)

    sql = """
    SELECT
        numero_set,
        pontos_jogador,
        pontos_adversario,
        vencedor
    FROM set_partida
    WHERE partida_id=%s
    ORDER BY numero_set ASC
    """

    cursor.execute(sql,(partida_id,))

    sets = cursor.fetchall()

    cursor.close()
    banco.close()

    return sets

def salvar_set(
    partida_id,
    numero_set,
    pontos_jogador,
    pontos_adversario,
    vencedor
):

    banco = conectar()
    cursor = banco.cursor()

    sql = """
    INSERT INTO set_partida
    (
        partida_id,
        numero_set,
        pontos_jogador,
        pontos_adversario,
        vencedor
    )

    VALUES
    (%s,%s,%s,%s,%s)
    """

    cursor.execute(
        sql,
        (
            partida_id,
            numero_set,
            pontos_jogador,
            pontos_adversario,
            vencedor
        )
    )

    banco.commit()

    cursor.close()
    banco.close()

def estatistica_partida(id):

    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    sql = """
    SELECT
    jogador,
    tecnica,
    SUM(resultado='Acerto') AS acertos,
    SUM(resultado='Erro') AS erros,
    ROUND(
        (
        SUM(resultado='Acerto') / COUNT(*)
        ) * 100,
        2
    ) AS aproveitamento
    FROM jogada
    WHERE partida_id=%s
    GROUP BY jogador, tecnica
    """

    cursor.execute(sql,(id,))
    estatisticas = cursor.fetchall()

    cursor.close()
    banco.close()

    return estatisticas