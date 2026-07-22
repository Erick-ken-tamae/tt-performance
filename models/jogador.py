from database import conectar


# Cadastrar jogador
def cadastrar_jogador(nome, idade, categoria, clube):

    banco = conectar()
    cursor = banco.cursor()

    sql = """
        INSERT INTO jogador
        (nome, idade, categoria, clube)
        VALUES (%s,%s,%s,%s)
    """

    valores = (
        nome,
        idade,
        categoria,
        clube
    )

    cursor.execute(sql, valores)

    banco.commit()

    cursor.close()
    banco.close()



# Listar jogadores
def listar_jogador():

    banco = conectar()
    cursor = banco.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM jogador"
    )

    jogadores = cursor.fetchall()

    cursor.close()
    banco.close()

    return jogadores



# Excluir jogador
def excluir_jogador(id):

    banco = conectar()
    cursor = banco.cursor()

    sql = """
        DELETE FROM jogador
        WHERE id=%s
    """

    cursor.execute(sql,(id,))

    banco.commit()

    cursor.close()
    banco.close()