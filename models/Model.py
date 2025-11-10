"""Implementações genéricas de CRUD reutilizáveis para tabelas do banco."""

from .modelBase import ModelBase


class Model(ModelBase):
    """Fornece operações CRUD básicas para uma tabela específica."""

    def __init__(self, connection, table_name, columns=None, primary_key='id'):
        """Configura a tabela, colunas selecionadas e chave primária padrão."""
        super().__init__(connection)
        self.table_name = table_name
        self.columns = columns
        self.primary_key = primary_key

    def prepare_create_data(self, data):
        """Permite ajustar os dados antes da inserção."""
        return data

    def prepare_update_data(self, data):
        """Permite ajustar os dados antes da atualização."""
        return data

    def create(self, data):
        """Insere um registro retornando o identificador gerado."""
        payload = self.prepare_create_data(dict(data))
        if not payload:
            raise ValueError('Dados para criação não podem ser vazios.')

        columns = ', '.join(payload.keys())
        placeholders = ', '.join(['?'] * len(payload))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, tuple(payload.values()))
        self.connection.commit()
        return self.cursor.lastrowid

    def read(self, record_id):
        """Recupera um único registro pela chave primária."""
        selected_columns = ', '.join(self.columns) if self.columns else '*'
        query = f"SELECT {selected_columns} FROM {self.table_name} WHERE {self.primary_key} = ?"
        self.cursor.execute(query, (record_id,))
        return self.cursor.fetchone()

    def get_all(self):
        """Retorna todos os registros existentes na tabela."""
        selected_columns = ', '.join(self.columns) if self.columns else '*'
        query = f"SELECT {selected_columns} FROM {self.table_name}"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update(self, record_id, data):
        """Atualiza campos do registro indicado."""
        payload = self.prepare_update_data(dict(data))
        if not payload:
            raise ValueError('Dados para atualização não podem ser vazios.')

        assignments = ', '.join(f"{column} = ?" for column in payload.keys())
        query = f"UPDATE {self.table_name} SET {assignments} WHERE {self.primary_key} = ?"
        params = tuple(payload.values()) + (record_id,)
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.rowcount

    def delete(self, record_id):
        """Remove um registro pela chave primária."""
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?"
        self.cursor.execute(query, (record_id,))
        self.connection.commit()
        return self.cursor.rowcount