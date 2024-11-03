from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for
from flask_cors import CORS
from pulp import LpVariable, LpProblem, lpSum, LpMinimize, value
import sys

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    # Obtener los datos del formulario
    puzzle = []
    for i in range(9):
        row = []
        for j in range(9):
            cell_value = request.form.get(f'cell_{i}_{j}', '').strip()
            if not cell_value:
                cell_value = '0'
            try:
                cell_value = int(cell_value)
                if cell_value < 0 or cell_value > 9:
                    return make_response("Los valores deben estar entre 0 y 9.", 400)
            except ValueError:
                return make_response("Todos los valores deben ser números enteros o dejados en blanco.", 400)
            row.append(cell_value)
        puzzle.append(row)

    # Validar la entrada
    if not isinstance(puzzle, list) or len(puzzle) != 9 or any(len(row) != 9 for row in puzzle):
        return make_response("Formato de puzzle inválido. Debe ser una matriz 9x9.", 400)

    # Inicializar el problema
    prob = LpProblem("Sudoku Problem", LpMinimize)

    # Crear las variables de decisión
    choices = LpVariable.dicts("Choice", (range(9), range(9), range(1, 10)), cat='Binary')

    # Añadir las restricciones
    for r in range(9):
        for c in range(9):
            prob += lpSum(choices[r][c][n] for n in range(1, 10)) == 1

    for r in range(9):
        for n in range(1, 10):
            prob += lpSum(choices[r][c][n] for c in range(9)) == 1

    for c in range(9):
        for n in range(1, 10):
            prob += lpSum(choices[r][c][n] for r in range(9)) == 1

    for br in range(3):
        for bc in range(3):
            for n in range(1, 10):
                prob += lpSum(choices[r + 3 * br][c + 3 * bc][n] for r in range(3) for c in range(3)) == 1

    # Establecer los valores iniciales para las celdas conocidas
    known_values = [(r, c, puzzle[r][c]) for r in range(9) for c in range(9) if puzzle[r][c] != 0]
    for r, c, n in known_values:
        prob += choices[r][c][n] == 1

    # Resolver el problema
    prob.solve()

    # Construir la solución
    solution = [[0 for _ in range(9)] for _ in range(9)]
    for r in range(9):
        for c in range(9):
            for n in range(1, 10):
                if value(choices[r][c][n]) == 1:
                    solution[r][c] = n

    return render_template('solution.html', puzzle=puzzle, solution=solution)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
