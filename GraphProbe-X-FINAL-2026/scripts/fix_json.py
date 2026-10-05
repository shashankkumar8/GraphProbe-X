import json
import pathlib

def fix_results(partial_path, output_path, pipeline):
    results = []
    with open(partial_path, encoding='utf-8') as f:
        for line in f:
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    output = {
        "pipeline": pipeline,
        "variant": "full",
        "split": "public",
        "model": "openai/gpt-4o-mini",
        "n": len(results),
        "results": results
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1, ensure_ascii=False)

    print(f"{pipeline}: {len(results)} rows -> {output_path}")

fix_results('results/agentic_results.partial.jsonl', 'results/agentic_results.json', 'agentic')
fix_results('results/rag_results.partial.jsonl', 'results/rag_results.json', 'rag')
