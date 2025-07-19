from datetime import datetime

# TODO
# deal with spechial char
# Jurídico > JurÃ\xaddico


# criados sintetico com LLM


def cast_to_date(date_str: str) -> datetime:
    """
    converts a string in the format "YYYY-MM-DD" to a Python datetime object.
    
    
    """
    return datetime.strptime(date_str, "%Y-%m-%d")

def reconcile_accounts(transactions1, transactions2):
    """matches transactions from transactions1 with those in transactions2"""
    used2 = [False] * len(transactions2)
# Tracks which rows in transactions2 have already been matched.
# Prevents one row from being used more than once.

    # For each row in transactions1, it tries to find a matching row in transactions2.
    for i, row1 in enumerate(transactions1):
        date1, dept1, val1, ben1 = row1
        date1 = cast_to_date(date1)
        candidates = []

        for j, row2 in enumerate(transactions2):
            if used2[j]:
                continue
            date2, dept2, val2, ben2 = row2
            date2_parsed = cast_to_date(date2)
                # To be considered a match, the row from transactions2 must:
                # Not be already used (used2[j] == False)
                # Have the same department (dept)
                # Have the same value
                # Have the same beneficiary
                # Be within 1 day (±1) of the date in transactions1
                # If all these match, it's added to the candidates list.
            if (
                dept1 == dept2
                and val1 == val2
                and ben1 == ben2
                and abs((date1 - date2_parsed).days) <= 1
            ):
                candidates.append((date2_parsed, j))

        # If multiple matches are found, it selects the one with the earliest date.
        # That row in both lists is labeled "FOUND" and marked as used.
        # If no match is found, mark the transaction in transactions1 as "MISSING".
        if candidates:
            # Sort by the earliest date
            _, best_match_index = sorted(candidates, key=lambda x: x[0])[0]
            transactions1[i].append("FOUND")
            transactions2[best_match_index].append("FOUND")
            used2[best_match_index] = True
        else:
            transactions1[i].append("MISSING")

    # Fill missing in out2
    # After matching, any row in transactions2 that wasn’t used is marked "MISSING".
    for j, used in enumerate(used2):
        if not used:
            transactions2[j].append("MISSING")

    return transactions1, transactions2

# print (reconcile_accounts (transactions1, transactions2))

# pode se tornar no futuro testes diferentes com pytest

def test_reconcile_accounts():
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

    for idx, case in enumerate(test_cases):
        out1, out2 = reconcile_accounts(case["list1"], case["list2"])
        assert out1 == case["expected1"], f"❌ {case["name"]} failed on list1"
        assert out2 == case["expected2"], f"❌ {case["name"]} failed on list2"
        print(f"✅ {case["name"]} passed")

# Example usage/test
if __name__ == "__main__":
    test_reconcile_accounts()