from datetime import datetime
from typing import List, Tuple, Dict, Optional, Set, Any


def cast_to_date(date_str: str) -> datetime:
    """
    Converte uma string no formato 'YYYY-MM-DD' para datetime.

    Args:
        date_str (str): Data no formato string
    
    Returns:
        
    """
    return datetime.strptime(date_str, "%Y-%m-%d")


def reconcile_accounts(transactions1: List[List], transactions2: List[List]) -> Tuple[List[List], List[List]]:
    """
    Concilia duas listas de transações com base em data (±1 dia), departamento,
    valor e beneficiário. Marca como 'FOUND' ou 'MISSING'.
    
    Args:
        transactions1 (list): Lista principal de transações.
        transactions2 (list): Lista de transações a serem comparadas.
    
    Returns:
        Tuple contendo as duas listas com os rótulos de conciliação.
    """
    used2 = [False] * len(transactions2)

    for i, row1 in enumerate(transactions1):
        date1, dept1, val1, ben1 = row1
        date1 = cast_to_date(date1)
        candidates = []

        for j, row2 in enumerate(transactions2):
            if used2[j]:
                continue

            date2_str, dept2, val2, ben2 = row2
            date2 = cast_to_date(date2_str)

            if (
                dept1 == dept2 and
                val1 == val2 and
                ben1 == ben2 and
                abs((date1 - date2).days) <= 1
            ):
                candidates.append((date2, j))

        if candidates:
            _, best_index = sorted(candidates, key=lambda x: x[0])[0]
            transactions1[i].append("FOUND")
            transactions2[best_index].append("FOUND")
            used2[best_index] = True
        else:
            transactions1[i].append("MISSING")

    for j, used in enumerate(used2):
        if not used:
            transactions2[j].append("MISSING")

    return transactions1, transactions2


def test_reconcile_accounts():
    """
    Executa testes unitários simples para verificar a lógica de reconciliação.
    """
    test_cases = [
        {
            "name": "Simple match ±1 day",
            "list1": [["2020-12-05", "Tecnologia", "50.00", "AWS"]],
            "list2": [["2020-12-06", "Tecnologia", "50.00", "AWS"]],
            "expected1": [["2020-12-05", "Tecnologia", "50.00", "AWS", "FOUND"]],
            "expected2": [["2020-12-06", "Tecnologia", "50.00", "AWS", "FOUND"]],
        },
        {
            "name": "No match, date difference > 1",
            "list1": [["2020-12-05", "Tecnologia", "50.00", "AWS"]],
            "list2": [["2025-01-03", "Tecnologia", "50.00", "AWS"]],
            "expected1": [["2020-12-05", "Tecnologia", "50.00", "AWS", "MISSING"]],
            "expected2": [["2025-01-03", "Tecnologia", "50.00", "AWS", "MISSING"]],
        },
        {
            "name": "Duplicate rows in both lists",
            "list1": [
                ["2020-12-05", "Tecnologia", "50.00", "AWS"],
                ["2020-12-05", "Tecnologia", "50.00", "AWS"],
            ],
            "list2": [
                ["2020-12-06", "Tecnologia", "50.00", "AWS"],
                ["2020-12-06", "Tecnologia", "50.00", "AWS"],
            ],
            "expected1": [
                ["2020-12-05", "Tecnologia", "50.00", "AWS", "FOUND"],
                ["2020-12-05", "Tecnologia", "50.00", "AWS", "FOUND"],
            ],
            "expected2": [
                ["2020-12-06", "Tecnologia", "50.00", "AWS", "FOUND"],
                ["2020-12-06", "Tecnologia", "50.00", "AWS", "FOUND"],
            ],
        },
        {
            "name": "Multiple possible matches — match oldest",
            "list1": [["2020-12-05", "Tecnologia", "50.00", "AWS"]],
            "list2": [
                ["2020-12-04", "Tecnologia", "50.00", "AWS"],
                ["2020-12-06", "Tecnologia", "50.00", "AWS"],
            ],
            "expected1": [["2020-12-05", "Tecnologia", "50.00", "AWS", "FOUND"]],
            "expected2": [
                ["2020-12-04", "Tecnologia", "50.00", "AWS", "FOUND"],
                ["2020-12-06", "Tecnologia", "50.00", "AWS", "MISSING"],
            ],
        },
        {
            "name": "Choose oldest match when exact date exists",
            "list1": [["2020-12-05", "Tecnologia", "50.00", "AWS"]],
            "list2": [
                ["2020-12-04", "Tecnologia", "50.00", "AWS"],
                ["2020-12-05", "Tecnologia", "50.00", "AWS"],
            ],
            "expected1": [["2020-12-05", "Tecnologia", "50.00", "AWS", "FOUND"]],
            "expected2": [
                ["2020-12-04", "Tecnologia", "50.00", "AWS", "FOUND"],
                ["2020-12-05", "Tecnologia", "50.00", "AWS", "MISSING"],
            ],
        },
        {
            "name": "Realistic example with some missing",
            "list1": [
                ["2020-12-04", "Tecnologia", "16.00", "Bitbucket"],
                ["2020-12-04", "Jurídico", "60.00", "LinkSquares"],
                ["2020-12-05", "Tecnologia", "50.00", "AWS"]
            ],
            "list2": [
                ["2020-12-04", "Tecnologia", "16.00", "Bitbucket"],
                ["2020-12-05", "Tecnologia", "49.99", "AWS"],
                ["2020-12-04", "Jurídico", "60.00", "LinkSquares"]
            ],
            "expected1": [
                ["2020-12-04", "Tecnologia", "16.00", "Bitbucket", "FOUND"],
                ["2020-12-04", "Jurídico", "60.00", "LinkSquares", "FOUND"],
                ["2020-12-05", "Tecnologia", "50.00", "AWS", "MISSING"]
            ],
            "expected2": [
                ["2020-12-04", "Tecnologia", "16.00", "Bitbucket", "FOUND"],
                ["2020-12-05", "Tecnologia", "49.99", "AWS", "MISSING"],
                ["2020-12-04", "Jurídico", "60.00", "LinkSquares", "FOUND"]
            ]
        }
    ]

    for case in test_cases:
        result1, result2 = reconcile_accounts(case["list1"], case["list2"])
        assert result1 == case["expected1"], f"❌ {case['name']} failed on list1"
        assert result2 == case["expected2"], f"❌ {case['name']} failed on list2"
        print(f"✅ {case['name']} passed")


if __name__ == "__main__":
    test_reconcile_accounts()
