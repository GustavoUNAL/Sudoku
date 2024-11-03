from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from pulp import LpVariable, LpProblem, lpSum, LpMinimize, value

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return "<h1>Hello, Welcome to VLESIM FBS!</h1>"

@app.route("/solve-sudoku", methods=['POST'])
def solve_sudoku():
    # Obtener los datos de entrada
    json_input = request.get_json()
    
    # Validar la entrada
    if 'puzzle' not in json_input:
        return make_response(jsonify({"error": "Missing 'puzzle' key in JSON input."}), 400)
    
    puzzle = json_input['puzzle']
    
    if not isinstance(puzzle, list) or len(puzzle) != 9 or any(len(row) != 9 for row in puzzle):
        return make_response(jsonify({"error": "Invalid puzzle format. Must be a 9x9 matrix."}), 400)

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

    return make_response(jsonify(solution), 200)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)