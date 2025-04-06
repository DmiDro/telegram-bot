from collections import Counter, defaultdict

def interpret_results(test_key, answers, TESTS):
    if test_key == "archetype":
        counter = Counter(answers)
        if not counter:
            return "unknown"
        max_count = max(counter.values())
        dominant = [k for k, v in counter.items() if v == max_count]
        return dominant[0]

    elif test_key == "emotional_maturity":
        score = sum(answers)
        if score <= 26:
            return "low"
        elif score <= 35:
            return "middle"
        else:
            return "high"

    elif test_key == "socionics":
        # Преобразование строковых ответов в дихотомии
        axis_map = {
            "extrovert": "E", "introvert": "I",
            "sensoric": "S", "intuitive": "N",
            "logical": "T", "ethical": "F",
            "rational": "J", "irrational": "P"
        }

        dimensions = defaultdict(int)
        for value in answers:
            code = axis_map.get(value.lower())
            if code:
                dimensions[code] += 1

        result_code = (
            ("E" if dimensions["E"] >= dimensions["I"] else "I") +
            ("S" if dimensions["S"] >= dimensions["N"] else "N") +
            ("T" if dimensions["T"] >= dimensions["F"] else "F") +
            ("J" if dimensions["J"] >= dimensions["P"] else "P")
        )

        return result_code

    elif test_key == "character":
        counter = Counter(answers)
        if not counter:
            return "unknown"
        return counter.most_common(1)[0][0]

    return "unknown"
