from database import conectar

def cadastrar_jogador(nome, idade, categoria, clube):
    banco = conectar()
    cursor = banco.cursor()
    
    sql= """
        INSERT INTO jogador
        (nome, idade, categoria, clube)
        VALUES
        (%s,%s,%s,%s)
    """
    
    valores=(nome, idade, categoria, clube)
    
    cursor.execute(sql, valores)
    
    banco.commit()
    cursor.close()
    banco.close()

def listar_jogador():
    banco = conectar()
    cursor = banco.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM jogador")
    
    jogadores = cursor.fetchall()
    
    cursor.close()
    banco.close()
    
    return jogadores
    