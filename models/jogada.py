from database import conectar
def listar_jogadas(id):
    banco = conectar()
    cursor = banco.cursor(dictionary=True)
    
    sql = """
        SELECT
            id,
            partida_id,
            numero_set,
            jogador,
            tecnica,
            resultado,
            observacao,
            data_registro
        FROM jogada
        WHERE partida_id = %s
        ORDER BY numero_set ASC, data_registro ASC;
    """
    
    cursor.execute(sql, (id,))
    
    jogadas = cursor.fetchall()
    
    cursor.close()
    banco.close()
    
    return jogadas